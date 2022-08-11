# import multiprocessing

bind = "0.0.0.0:5000"

workers = 1  # multiprocessing.cpu_count() * 2 + 1
max_requests = 1000
timout = 45
