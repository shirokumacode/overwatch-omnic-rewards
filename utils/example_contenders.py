import time, sys

import checker as checker
from viewer import Viewer


ACCOUNT_ID = 123456789
MIN_BETWEEN_CHECKS = 10
CONTENDERS_FLAG = True

def main():
    while True:
        print("Check OWC page")
        video_player = checker.check_page_islive(contenders=CONTENDERS_FLAG)
        if video_player:
            print("\tVideo is Live")
            viewer = Viewer(ACCOUNT_ID, video_player["video"]['id'], video_player["uid"], contenders=CONTENDERS_FLAG)
            try:
                while viewer.send_sentinel_packets(): 
                    print(".", end="", flush=True)
                    time.sleep(60)
                    viewer.time_watched += 1
            except KeyboardInterrupt:
                print("\n\tWatched {} minutes".format(str(viewer.time_watched)))
                sys.exit()
            print("\n\tWatched {} minutes".format(str(viewer.time_watched)))

        print("Sleeping for now")
        time.sleep(MIN_BETWEEN_CHECKS * 60)

if __name__ == "__main__":
    main()