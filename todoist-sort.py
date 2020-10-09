from todoist.api import TodoistAPI
import os
import json
import datetime 
import re
  

def getTasksInProject(intPojectID,items):
        projectItems = []
        for thisItem in items:
                if thisItem['project_id'] == intPojectID:
                        #print("This item:"+ thisItem['content']+", child order:"+str(thisItem['child_order']))
                        dictItem = {
                                "id":thisItem['id'],
                                "content":thisItem['content'],
                                "due":thisItem['due'],
                                "priority":thisItem['priority'],
                                "child_order":thisItem['child_order']
                                }
                        projectItems.append(dictItem)
        #Now sort to reflect the view of the live application by respecting existing child order
        #Refactor below to function
        exchanges = True
        passnum = len(projectItems)-1
        while passnum > 0 and exchanges:
                exchanges = False
                for i in range(passnum):
                        if projectItems[i]['child_order'] > projectItems[i+1]['child_order']:
                                exchanges = True
                                #print("Swapping:"+ tasks[i]['content'])
                                #print("For:"+ tasks[i+1]['content'])
                                temp = projectItems[i]
                                projectItems[i] = projectItems[i+1]
                                projectItems[i+1] = temp
                passnum = passnum-1
        return projectItems

def sortTasks(tasks,sortBy):
        tupleSortOptions = ("name", "due", "priority")
        strFindLinks = r"\[([^\]\[]*)\]\(([^\]\[]*)\)"

        if sortBy.lower() in tupleSortOptions:
                if sortBy.lower() == "name":
                        print("===Start sorting by name===")
                        #do something
                        exchanges = True
                        passnum = len(tasks)-1
                        while passnum > 0 and exchanges:
                                exchanges = False
                                for i in range(passnum):
                                        #Clean content
                                        strThisTaskContent = tasks[i]['content'].lower()
                                        strThisTaskContent = re.sub(strFindLinks, r"\1" ,strThisTaskContent)
                                        strNextTaskContent = tasks[i+1]['content'].lower()
                                        strNextTaskContent = re.sub(strFindLinks, r"\1" ,strNextTaskContent)

                                        if strThisTaskContent>strNextTaskContent:
                                                exchanges = True
                                                #print("Swapping:"+ tasks[i]['content'])
                                                #print("For:"+ tasks[i+1]['content'])
                                                temp = tasks[i]
                                                tasks[i] = tasks[i+1]
                                                tasks[i+1] = temp

                                passnum = passnum-1

                        print("===Done sorting by name===")
                elif sortBy.lower() == "due":
                        print("===Start sorting by due===")
                        exchanges = True
                        passnum = len(tasks)-1
                        while passnum > 0 and exchanges:
                                exchanges = False
                                for i in range(passnum):
                                        #print("Evaluation of:"+ tasks[i]['content']+":"+str(tasks[i]['due']['date']))
                                        #print("Against:"+ tasks[i+1]['content']+":"+str(tasks[i+1]['due']['date']))
                                        if tasks[i]['due'] is None and tasks[i+1]['due'] is not None:
                                                #This task has no date, but the next one does. Swap.
                                                exchanges = True
                                                #print("Swapping:"+ tasks[i]['content'])
                                                #print("For:"+ tasks[i+1]['content'])
                                                temp = tasks[i]
                                                tasks[i] = tasks[i+1]
                                                tasks[i+1] = temp
                                        elif tasks[i+1]['due'] is None:
                                                #tasks[i]['due'] result doesn't matter if the next task has no date
                                                #Do nothing
                                                print("Task without a date:do nothing")
                                                #print("Not swapping:"+ tasks[i]['content'])
                                                #print("For:"+ tasks[i+1]['content'])
                                        elif tasks[i]['due']['date'] > tasks[i+1]['due']['date']:
                                                #both this task has a data and so does the next
                                                exchanges = True
                                                #print("Swapping:"+ tasks[i]['content'])
                                                #print("For:"+ tasks[i+1]['content'])
                                                temp = tasks[i]
                                                tasks[i] = tasks[i+1]
                                                tasks[i+1] = temp
                                passnum = passnum-1
                elif sortBy.lower() == "priority":
                        #sort by priority
                        #The priority of the task (a number between 1 and 4, 4 for very urgent and 1 for natural).
                        print("===Start sorting by priority===")
                        exchanges = True
                        passnum = len(tasks)-1
                        while passnum > 0 and exchanges:
                                exchanges = False
                                for i in range(passnum):
                                        if tasks[i]['priority'] < tasks[i+1]['priority']:
                                                exchanges = True
                                                print("Swapping:"+ tasks[i]['content'])
                                                print("For:"+ tasks[i+1]['content'])
                                                temp = tasks[i]
                                                tasks[i] = tasks[i+1]
                                                tasks[i+1] = temp
                                passnum = passnum-1
                        print("===Done sorting by priority===")
                #Assume sorted, return tasks
                return tasks
        else:
                raise Exception("Sort option not understood")


def main():
    print("Loading config...")
    with open('/home/pi/todoist-ordering/config.json', 'r') as f:
        config = json.load(f)
    api = TodoistAPI(config['apikey'])
    api.sync()
    projects_to_sort = config['projects']
    print("Sorting projects")
    for project in api.state['projects']:
        name = project['name']
        if name in projects_to_sort.keys():
            sortkeys = projects_to_sort[name]
            result = getTasksInProject(project['id'],api.state['items'])
        #     for item in result:
        #         print("Item Content: (" + item['content'] + ")")
            for sortkey in sortkeys:
                sortedResult = sortTasks(result,sortkey)
                print("Sorting project: '" + project['name'] + "' by key: '" + sortkey + "'")
            thisOrder=0
            for item in sortedResult:
                api.items.reorder([{'id': item['id'], 'child_order': thisOrder}])
                thisOrder +=1
        #     print("After sort...")
        #     for item in result:
        #         print("Item Content: (" + item['content'] + ")")
            print("Committing...")
        else:
            print("No config for project: '" + project['name'] + "'")
        
    api.commit()
    print("DONE!")


if __name__ == "__main__":
    main()