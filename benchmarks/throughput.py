import time

from blockchain_core.runtime import BlockchainRuntime


def measure_throughput(tx_count=200):

    runtime = BlockchainRuntime()

    start = time.time()

    runtime.run(tx_count)

    end = time.time()

    duration = end - start

    tps = tx_count / duration

    print("\n====================")
    print("Transactions:", tx_count)
    print("Time:", duration)
    print("TPS:", tps)
    print("====================")


if __name__ == "__main__":
    measure_throughput(200)