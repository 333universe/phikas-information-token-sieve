# phikas_engine/core/engine.py
"""
PhiKas Information/Token Sieve (v2.0.0) Core Engine
Optimized for modular package distribution.
Handles token-normalized log audit and chronological modeling pipelines.
"""

import json
import re
import os
import sys
import argparse
import subprocess
from datetime import datetime

class PhiKasEngineV2:
    def __init__(self, total_steps=10000, max_context_chars=4096, similarity_threshold=0.82, ignore_categories=None):
        self.total_steps = total_steps
        self.max_context_chars = max_context_chars
        self.similarity_threshold = similarity_threshold
        # Normalize ignore list to uppercase for clean matching
        self.ignore_categories = {cat.upper() for cat in ignore_categories} if ignore_categories else set()
        
        # Core linguistic stop words to discard during tokenization
        self.stop_words = {'on', 'across', 'detected', 'the', 'after', 'with', 'for', 'at', 'by', 'of', 'and'}

    def _normalize_and_tokenize(self, text):
        """Lowercase text, strip punctuation, discard stop words, and return unique tokens."""
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = set(clean_text.split())
        return tokens - self.stop_words

    def _calculate_token_ratio(self, tokens_a, tokens_b):
        """Calculates (Shared Unique Words) / (Total Unique Words in the shorter description)"""
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a.intersection(tokens_b)
        min_length = min(len(tokens_a), len(tokens_b))
        return len(intersection) / min_length if min_length > 0 else 0.0

    def process_run(self, raw_log_lines):
        """Executes the core 4-stage processing lifecycle of the Token Sieve."""
        audit_trail = {"accepted_structured": [], "accepted_unstructured": [], "rejected": [], "exact_duplicates": []}
        timeline_groups = {}
        related_incident_review_flags = []
        seen_lookup = {}
        parsed_tickets = []

        # Lifecycle Stage 1 & 2: Ingestion, Deduplication, and Structured Pattern Parsing
        for index, line in enumerate(raw_log_lines):
            line = line.strip()
            if not line:
                continue
                
            # Enforce line capacity and control character constraints
            if len(line) > self.max_context_chars or any(ord(c) < 32 and c not in '\n\r\t' for c in line):
                audit_trail["rejected"].append({"index": index, "raw": line, "reason": "Length or control character violation"})
                continue
                
            # Deduplicate incoming identical record matrices
            if line in seen_lookup:
                audit_trail["exact_duplicates"].append({"index": index, "first_input_index": seen_lookup[line]})
                continue
            
            seen_lookup[line] = index
            parts = [p.strip() for p in line.split('|')]
            
            # Structural Schema Splitting: YYYY-MM-DD | ticket_id | category | description
            if len(parts) == 4 and re.match(r'^\d{4}-\d{2}-\d{2}$', parts[0]) and re.match(r'^[\w\.\-_]+$', parts[1]):
                date, ticket_id, category, description = parts
                category_upper = category.upper()
                
                # Dynamic Command Line Ignore Filter Check
                if category_upper in self.ignore_categories:
                    continue
                    
                audit_trail["accepted_structured"].append(line)
                parsed_tickets.append({
                    "index": index, "date": date, "ticket_id": ticket_id, 
                    "category": category_upper, "description": description, "tokens": self._normalize_and_tokenize(description)
                })
            else:
                severity_match = re.search(r'\b(CRITICAL|WARN|ERROR|INFO|ALERT)\b', line, re.IGNORECASE)
                extracted_severity = severity_match.group(1).upper() if severity_match else "UNKNOWN"
                
                # Filter out unstructured logs matching ignored severities/keywords
                if extracted_severity in self.ignore_categories:
                    continue
                    
                audit_trail["accepted_unstructured"].append({
                    "index": index, "raw": line, "metadata": {"extracted_severity": extracted_severity}
                })

        # Lifecycle Stage 3: Timeline Group Modeling
        for ticket in parsed_tickets:
            t_id = ticket["ticket_id"]
            if t_id not in timeline_groups:
                timeline_groups[t_id] = []
            timeline_groups[t_id].append({
                "date": ticket["date"], "category": ticket["category"], "description": ticket["description"], "_tokens": ticket["tokens"]
            })
            
        for t_id in timeline_groups:
            timeline_groups[t_id].sort(key=lambda x: x["date"])

        # Lifecycle Stage 4: Cross-Ticket Heuristic Review (Token-Normalized Sieve)
        ticket_ids = list(timeline_groups.keys())
        for i in range(len(ticket_ids)):
            for j in range(i + 1, len(ticket_ids)):
                t1, t2 = ticket_ids[i], ticket_ids[j]
                for entry1 in timeline_groups[t1]:
                    for entry2 in timeline_groups[t2]:
                        if entry1["category"] == entry2["category"]:
                            ratio = self._calculate_token_ratio(entry1["_tokens"], entry2["_tokens"])
                            if ratio >= self.similarity_threshold:
                                shared_tokens = sorted(list(entry1["_tokens"].intersection(entry2["_tokens"])))
                                related_incident_review_flags.append({
                                    "type": "POSSIBLY_RELATED_REVIEW", "source_ticket": t1, "target_ticket": t2,
                                    "calculated_token_ratio": round(ratio, 4), "matching_tokens": shared_tokens,
                                    "reason": "Token intersection meets threshold boundary criteria within identical category."
                                })

        # Cleanup internal comparison tokens from the final layout payload
        for t_id in timeline_groups:
            for entry in timeline_groups[t_id]:
                entry.pop("_tokens", None)

        return {
            "status": "COMPLETED",
            "instance_parameters": {
                "total_steps": self.total_steps, 
                "max_context_chars": self.max_context_chars, 
                "related_similarity_threshold": self.similarity_threshold,
                "ignored_categories_applied": list(self.ignore_categories)
            },
            "audit_trail": audit_trail, "timeline_groups": timeline_groups, "related_incident_review_flags": related_incident_review_flags
        }

def run_manual_git_sequence(filename):
    """Interactive Git routine to facilitate manual uploads to GitHub from terminal environments."""
    print("\n========= PHIKAS MANUAL DEPLOYMENT SEQUENCE =========")
    confirm = input(f"Would you like to manually upload '{filename}' to GitHub right now? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Skipping Git deployment. Local payload remains saved.")
        return
    try:
        if not os.path.isdir(".git"):
            print("❌ Error: Active directory is not a Git repository. Run 'git init' first.")
            return
        subprocess.run(["git", "add", filename], check=True)
        commit_msg = input("Enter custom commit message (or press enter for default timestamp): ").strip()
        if not commit_msg:
            commit_msg = f"PhiKas Engine Run Manifest: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            commit_msg = f"PhiKas Engine: {commit_msg}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Success! Manifest uploaded manually to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git Manual Push Deployment aborted: {e}")
    print("=====================================================")

# Main execution orchestrator
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PhiKas Information/Token Sieve Command Line Interface")
    parser.add_argument("file", nargs="?", help="Optional path to log text file to parse directly")
    parser.add_argument("-i", "--ignore", nargs="+", help="Space-separated list of log categories or severities to ignore")
    args = parser.parse_args()

    dataset = []

    # Direct automated ingestion routing
    if not sys.stdin.isatty():
        dataset = sys.stdin.read().splitlines()
    elif args.file:
        if os.path.exists(args.file):
            with open(args.file, "r") as f:
                dataset = f.splitlines()
        else:
            print(f"❌ Target path error: File '{args.file}' not found.")
            sys.exit(1)
    else:
        print("=====================================================")
        print("💬 PhiKas Token Sieve: Paste log dataset lines below.")
        print("   (When finished, type 'END' on a new line and press enter)")
        print("=====================================================")
        while True:
            try:
                line = input()
                if line.strip() == "END":
                    break
                dataset.append(line)
            except EOFError:
                break

    if not dataset:
        print("⚠ Operational Warning: Received empty stream dataset array. Execution cancelled.")
        sys.exit(0)

    # Process logs, write output manifest locally
    engine = PhiKasEngineV2(ignore_categories=args.ignore)
    output_json = engine.process_run(dataset)
    
    output_filename = "phikas_output.json"
    with open(output_filename, "w") as f:
        json.dump(output_json, indent=2, fp=f)
