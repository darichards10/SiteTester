import subprocess
import sys

def run_load_Test(urls, users, rampuptime, holdtime):
    try:
        subprocess.run(["python", "loadtester.py", urls, users, rampuptime, holdtime], check=True)
        print("Load test completed successfully!")
    except subprocess.CalledProcessError:
        print("An error occurred while running the load test.")

def run_site_test(site_name, output_name):
    try:
        subprocess.run(["python", "SiteTester.py", site_name, output_name], check=True)
        print("Site test completed successfully!")
    except subprocess.CalledProcessError:
        print("An error occurred while running the site test.")

def run_report_builder():
    try:
        subprocess.run(["python", "ReportBuilder.py"], check=True)
        print("Report Builder completed successfully!")
    except subprocess.CalledProcessError:
        print("An error occurred while running the report builder.")

if __name__ == "__main__":
    try:
        print("Running site tests...")
        run_site_test(str(sys.argv[1]), "sitetestresults.csv")
        run_load_Test("sitetestresults.csv", str(sys.argv[2]), str(sys.argv[3]), str(sys.argv[4]))
        run_report_builder()
    except Exception:
        print("Error")