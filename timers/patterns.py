from toothless import path
from . import sprint as s

prefix_patterns = [
    path('<endtime:date*>', s.start_sprint),
    path('start <endtime:date*>', s.start_sprint),
    path('stop <sprintid:int>', s.stop_sprint),
    path('join <sprintid:int>', s.join_sprint),
    path('giveup', s.leave_sprint)
]
