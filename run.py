import multiprocessing
import time

from walnut.runners import adminBotRunner, botRunner, presentationRunner


def run_with_retry(function, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            function()
        except Exception:
            time.sleep(3)
        retries += 1
    return False


def main():
    processes = []
    runners = [botRunner, adminBotRunner, presentationRunner]

    for runner in runners:
        process = multiprocessing.Process(target=run_with_retry, args=[runner])
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
