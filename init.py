import json
import argparse

"""scrum nanny, helps you keep your sprint commitment safe"""
def init():
    json_file = open('settings.json')

    settings = json.load(json_file)
    #print("First project name is %s" % (settings["projects"][0]["name"]))
    json_file.close()

    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="project's name, as stated in your config")
    parser.add_argument("-i", "--sprint-index", help="sprint index, as stated in your config")
    args = parser.parse_args()
    print args.project
    print args.sprint_index

if __name__ == '__main__':
    init()

