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

    def parse_coverage_output(self, output):
        pattern = r"(src/.*?)\s+(\d+)\s+(\d+)\s+(\d+%)\s+(.*)"
        matches = re.findall(pattern, output)

        return [
            {
                "Name": match[0],
                "Stmts": match[1],
                "Miss": match[2],
                "Cover": match[3],
                "Missing": match[4],
            }
            for match in matches
        ]

    def save_to_csv(self, data):
        with open(self.output_filename, "w", newline="") as csvfile:
            fieldnames = ["Name", "Stmts", "Miss", "Cover", "Missing"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in data:
                writer.writerow(row)

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
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running pytest: {e}")
            logger.error(e.stdout)
            logger.error(e.stderr)
            sys.exit(1)

    # @staticmethod
    def run(self):
        pytest_output = self.run_pytest()
        logger.info(pytest_output)
        coverage_data = self.parse_coverage_output(pytest_output)
        self.save_to_csv(coverage_data)


if __name__ == "__main__":
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    runner = PytestCoverageRunner()
    runner.run()
