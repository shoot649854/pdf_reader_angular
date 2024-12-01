import csv
import os
import re
import subprocess
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
import os

from src.logging.Logging import logger

FolderYear = datetime.datetime.now().strftime("%Y")
FolderDate = datetime.datetime.now().strftime("%m-%d")
LogFileName = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

DATALOG_FILE_PATH = f"test_log/{LogFileName}"
os.makedirs(os.path.dirname(DATALOG_FILE_PATH), exist_ok=True)


class PytestCoverageRunner:
    def __init__(self, output_filename=DATALOG_FILE_PATH):
        self.output_filename = output_filename
        self.total_tests = 0  # Initialize total tests count

    def parse_coverage_output(self, output):
        pattern = r"(src/.*?)\s+(\d+)\s+(\d+)\s+(\d+%)\s+(.*)"
        matches = re.findall(pattern, output)

        return [
            {
                "Name": match[0],
                "Statements": int(match[1]),  # Convert to integer
                "Miss": int(match[2]),  # Convert to integer
                "Cover": match[3],
                "Missing": match[4],
            }
            for match in matches
        ]

    def calculate_totals(self, coverage_data):
        total_stmts = sum(item["Statements"] for item in coverage_data)
        total_miss = sum(item["Miss"] for item in coverage_data)
        total_cover = f"{(1 - total_miss / total_stmts) * 100:.2f}%" if total_stmts else "0%"
        return {
            "Name": "TOTAL",
            "Statements": total_stmts,
            "Miss": total_miss,
            "Cover": total_cover,
            "Missing": "",
            "Total Tests": self.total_tests,  # Add total tests to the totals row
        }

    def save_to_csv(self, data):
        with open(self.output_filename, "w", newline="") as csvfile:
            fieldnames = [
                "Name",
                "Statements",
                "Miss",
                "Cover",
                "Missing",
                "Total Tests",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in data:
                writer.writerow(row)

        logger.info(f"Coverage data saved to {self.output_filename}")

    def save_to_csv_with_total(self, data):
        total_row = self.calculate_totals(data)
        data.insert(0, total_row)  # Add totals as the first row

        with open(self.output_filename, "w", newline="") as csvfile:
            fieldnames = [
                "Name",
                "Statements",
                "Miss",
                "Cover",
                "Missing",
                "Total Tests",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(data)

        logger.info(f"Coverage data saved to {self.output_filename}")

    def run_pytest(self):
        command = [
            "poetry",
            "run",
            "pytest",
            "test",
            "-vv",
            "--tb=short",
            "-s",
            "--cov-report=term-missing",
            "--cov=src",
            "--color=yes",
        ]

        try:
            with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            ) as proc:
                output_lines = []
                for line in proc.stdout:
                    sys.stdout.write(line)  # Display output in real-time
                    output_lines.append(line)
                proc.wait()
                if proc.returncode != 0:
                    logger.error(f"Error running pytest: Return code {proc.returncode}")
                    sys.exit(proc.returncode)

                # Extract total number of tests from pytest output
                self.total_tests = self.extract_total_tests(output_lines)
                return "".join(output_lines)

        except Exception as e:
            logger.error(f"Exception running pytest: {e}")
            sys.exit(1)

    def extract_total_tests(self, output_lines):
        for line in output_lines:
            if re.search(r"(\d+)\s+(passed|failed|skipped)", line):
                match = re.findall(r"(\d+)\s+(passed|failed|skipped)", line)
                total_tests = sum(int(m[0]) for m in match)
                return total_tests
        return 0

    def run(self):
        pytest_output = self.run_pytest()
        logger.debug(pytest_output)
        coverage_data = self.parse_coverage_output(pytest_output)
        self.save_to_csv_with_total(coverage_data)


if __name__ == "__main__":
    runner = PytestCoverageRunner()
    runner.run()
