import datetime
import json
import pickle
from typing import Any, List
from dateutil import parser
import pandas as pd
import requests
import urllib3
from jira import JIRA

urllib3.disable_warnings()

# The BPMN-RPA Jira module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Jira module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA Jira module is based on the Jira Python module, which is licensed under the BSD 2-Clause "Simplified" License:
# Copyright (c) 2012, Atlassian Pty Ltd.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class Jira:

    # Class for reading, creating and editing van Jira Issues
    # Go to https://admin.atlassian.com to get your API token

    def __init__(self, jira_user: str, jira_pwd: str, jira_url: str):
        """
        Initiation of the JiraObject.
        :param jira_user: The username for logging into Jira.
        :param jira_pwd: The password for logging into Jira.
        :param jira_url: The URL of the Jira instance.
        """
        self.rooturl = jira_url
        self.options = {'server': self.rooturl}
        self.jira_user = jira_user
        self.jira_pwd = jira_pwd
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to Jira.
        """
        self.jira = JIRA(options=self.options, basic_auth=(self.jira_user, self.jira_pwd))

    def __is_picklable__(self, obj: any) -> bool:
        """
        Internal function to determine if the object is pickable.
        :param obj: The object to check.
        :return: True or False
        """
        try:
            pickle.dumps(obj)
            return True
        except Exception as e:
            return False

    def __getstate__(self):
        """
        Internal function for serialization
        """
        state = self.__dict__.copy()
        for key, val in state.items():
            if not self.__is_picklable__(val):
                state[key] = str(val)
        return state

    def __setstate__(self, state):
        """
        Internal function for deserialization
        :param state: The state to set to the 'self' object of the class
        """
        self.__dict__.update(state)
        self.__connect__()

    def get_issue(self, issue_key: str) -> Any:
        """
        Retreive a specific issue from Jira.
        :param issue_key: The issue key of the issue to retreive.
        :return: An Issue object.
        """
        return self.jira.issue(issue_key)

    def get_last_comment(self, issue_key: str) -> any:
        """
        Retreive the last comment that was added to the issue.
        :param issue_key: The issue key of the issue to retreive the last comment of.
        :return: The last comment of the Issue.
        """
        comments = self.jira.comments(issue_key)
        try:
            ret = comments[len(comments) - 1]
        except (ValueError, Exception):
            ret = None
        return ret

    def delete_issue(self, issue_key: str):
        """
        Delete a specific Issue from Jira.
        :param issue_key: The issue key of the issue to delete.
        :return: True when deleted without errors, otherwise False.
        """
        try:
            issue = self.get_issue(issue_key)
            issue.delete()
            ret = True
        except (ValueError, Exception):
            ret = False

    def get_issues(self, project: str) -> list:
        """
        Retreive a list of all issues of a project from Jira.
        :param project: The project key to retreive all issues of.
        :return: A list with Issue objects of all issues.
        """
        issues = []
        i = 0
        chunk_size = 100
        while True:
            chunk = self.jira.search_issues(f'project = {project}', startAt=i, maxResults=chunk_size)
            i += chunk_size
            issues += chunk.iterable
            if i >= chunk.total:
                break
        return issues

    def get_all_sprints(self, board_id: int) -> any:
        """
        Get a list of all sprint objects from a specific board in Jira.
        :param board_id: The board ID to get all sprints of.
        :return: A list containing all sprints belonging to the board.
        """
        sprints = self.jira.sprints(board_id)
        return sprints

    def get_issues_by_jql(self, jql: str) -> List:
        """
        Retreive a List of Issues by query in the Jira Query Language (jql).
        :param jql: The JQL query to execute.
        :return: A list of Issue objects.
        """
        block_size = 100
        block_num = 0
        ret = []
        while True:
            start_idx = block_num * block_size
            url = f"{self.rooturl}/rest/api/2/search?jql={jql}&startAt={start_idx}&maxResults={block_size}"
            json_result = requests.get(url, verify=True, auth=(self.jira_user, self.jira_pwd))
            issues = json.loads(json_result.text)["issues"]
            if len(issues) == 0:
                # Retrieve issues until there are no more to come
                break
            block_num += 1
            for issue in issues:
                ret.append(issue)
        return ret

    def get_epics(self, project: str) -> List:
        """
        Retreive a list of Epics for a specific project.
        :param project: The Project Key to retrieve the Epics of.
        :return: A list of Epics.
        """
        epics = self.jira.search_issues(f'project = {project} AND issuetype = Epic', maxResults=1000)
        return epics

    def create_issue_if_not_already_in_sprint(self, projectkey: str, summary: str, description: str, issuetype: str = "Story") -> any:
        """
        Create an issue only if it is not already in the current sprint.
        :param projectkey: The Project Key.
        :param summary: The summary of the issue to create.
        :param description: The description of the issue to create.
        :param issuetype: The issue type of the issue to create.
        :return: the issue object.
        """
        if description == "":
            description = None
        iss = self.get_issues_in_sprint(projectkey)
        for i in iss:
            fields = i.get("fields")
            if fields.get("summary") == summary and fields.get("description") == description and fields.get("issuetype").get("name") == issuetype:
                return ""
        return self.create_issue(projectkey, summary, description, issuetype)

    def create_issue(self, projectkey: str, summary: str, description: str, issuetype: str = "Story") -> any:
        """
        Create an Issue for a specific Project in Jira.
        :param projectkey: The Project Key.
        :param summary: The summary of the issue to create.
        :param description: The description of the issue to create.
        :param issuetype: The issue type of the issue to create.
        :return: the JSON result of the request.
        """
        issue = self.jira.create_issue(project=projectkey, summary=summary, description=description, issuetype={"name": issuetype})
        return issue

    def update_story_points(self, issuekey: str, storypoints: str, storypoints_field="customfield_10106") -> str:
        """
        Update the Story Points of an Issue in Jira.
        :param issuekey: The IssueKey of the Issue to update.
        :param storypoints: The new value for the Story Points of the Issue.
        :param storypoints_field: The field name of the Story Points field.
        :return: The JSON result of the request.
        """
        s_data = {"fields": {storypoints_field: storypoints}}
        url = f"{self.rooturl}/rest/api/2/issue/{issuekey}"
        json_result = requests.put(url, verify=True, json=s_data, auth=(self.jira_user, self.jira_pwd))
        return json.loads(json_result.content)

    def add_component(self, issue_key: str, component_name: str) -> any:
        """
        Add a component to an Issue in Jira.
        :param issue_key: The IssueKey of the Issue to update.
        :param component_name: The name of the component to add.
        :return: The issue object.
        """
        issue = self.jira.issue(issue_key)
        issue.update(fields={"components": [{"name": component_name}]})
        return issue

    def remove_component(self, issue_key: str, component_name: str) -> any:
        """
        Remove components of an Issue in Jira.
        :param issue_key: The IssueKey of the Issue to update.
        :param component_name: The name of the component to remove.
        :return: The issue object.
        """
        issue = self.jira.issue(issue_key)
        issue.update(fields={"components": [{"remove": {"name": component_name}}]})
        return issue

    def remove_issues_from_component(self, project_key: str, component_name: str):
        """
        Remove the link between an Component and all of its linked Issues.
        :param project_key: The ProjectKey of the project in Jira.
        :param component_name: The component name.
        """
        issues = self.get_issues_with_same_component_by_component_name(project_key, component_name)
        for iss in issues:
            result = self.remove_component(iss["key"], component_name)

    def get_transitions(self, issuekey: str) -> List:
        """
        Get the transitions of a specific Issue in Jira.
        :param issuekey: The IssueKey of the Issue to retreive the transitions of.
        :return: A list of transitions of the Issue.
        """
        transitions = self.jira.transitions(issuekey)
        return transitions

    def transition_issue(self, issuekey: str, id_: str) -> any:
        """
        Push an Issue to the next transition phase.
        :param issuekey: The IssueKey of the Issue.
        :param id_: The ID of the transition to push.
        :return: The issue object.
        """
        issue = self.jira.issue(issuekey)
        issue.transition_issue(id_)
        return issue

    def close_issue(self, issuekey: str):
        """
        Cloas a specific Issue in Jira.
        :param issuekey: The IssueKey of the Issue to close.
        """
        i = self.get_issue(issuekey)
        transitions = self.get_transitions(issuekey)
        check = i["fields"]["status"]["name"]
        found = False
        for trans in transitions:
            name = trans["name"]
            if found:
                id_ = trans["id"]
                self.transition_issue(issuekey, id_)
            if name == check:
                found = True

    def add_comment(self, issuekey: str, text: str) -> any:
        """
        Add a comment to an Issue in Jira.
        :param issuekey: The IssueKey of the Issue to add the comment to.
        :param text: The text of the comment to add to the Issue.
        :return: The issue object.
        """
        issue = self.jira.issue(issuekey)
        issue.add_comment(text)
        return issue

    def delete_comment(self, issuekey: str, commentid: str) -> any:
        """
        Delete a comment from an Issue in Jira.
        :param issuekey: The IssueKey of the Issue to delete the comment from.
        :param commentid: The ID of the comment to delete.
        :return: The issue object.
        """
        issue = self.jira.issue(issuekey)
        issue.delete_comment(commentid)
        return issue

    def assign_issue(self, issuekey: str, name: str) -> any:
        """
        Assigna an Issue to a user in Jira.
        :param issuekey: The IssueKey of the Issue to assign.
        :param name: The name of the user to assign the Issue to.
        :return: The issue object.
        """
        issue = self.jira.issue(issuekey)
        issue.update(assignee={"name": name})
        return issue

    def get_issues_in_sprint(self, projectkey: str) -> List:
        """
        Retreive a List of all Issues in the current Sprint of a specific Project.
        :param projectkey: The Project Key of the Jira Project.
        :return: A list of all Issues that are in the current Sprint of the Project.
        """
        return self.jira.search_issues(f"project={projectkey} and sprint in openSprints() and sprint not in futureSprints() and issuetype!=Epic and status not in (done) order by key", maxResults=False)

    def get_issues_in_sprint_including_done(self, projectkey: str) -> List:
        """
        Retreive a List of all Issues (including Issues with status 'Done') in the current Sprint of a specific Project.
        :param projectkey: The Project Key of the Jira Project.
        :return: A list of all Issues that are in the current Sprint of the Project.
        """
        return self.jira.search_issues(f"project={projectkey} and sprint in openSprints() and sprint not in futureSprints() and issuetype!=Epic order by key", maxResults=False)

    def get_issues_with_same_component_by_component_name(self, projectkey: str, component_name: str) -> List:
        """
        Retreive a List of all Issues that have the same component in a specific Project.
        :param projectkey: The Project Key of the Jira Project.
        :param component_name: The name of the component to get the issues of.
        :return: A list of all Issues that have the same component.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and component ='{component_name}' order by key", maxResults=False)

    def get_sprint_id(self, boardname: str) -> any:
        """
        Retreive the Sprint ID of the Current Sprint.
        :param boradname: The name of the board to get the Sprint ID of.
        :return: The ID of the current Sprint.
        """
        board_id = self.jira.boards(maxresults=999, name=boardname)[0].id
        sprint_id = self.jira.sprints(board_id, state="active")[0].id
        return id

    def move_issues_from_epic_to_epic(self, projectkey: str, oldepickey: str, newepickey: str):
        """
        Move all Issues form a specific Epic to another Epic.
        :param projectkey: The ProjectKey of the project that contains the Issues.
        :param oldepickey: The Epic Key of the Epic that currently holds the Issues.
        :param newepickey: The Epic Key of the target Epic to move the Issues to.
        """
        issues = self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and epic={oldepickey} order by key", maxResults=False)
        for iss in issues:
            self.jira.add_issues_to_epic(newepickey, iss.key)
            print(f"Issue {iss.key} verplaatst naar Epic {newepickey}")

    def get_issues_in_backlog(self, projectkey: str) -> List:
        """
        Retreive all Issues of a Project that are currently in the Backlog.
        :param projectkey: The ProjectKey of the Project.
        :return: A list of all Issues that are currently in the Backlog.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status not in (done) and sprint not in openSprints() and sprint not in futureSprints() order by key", maxResults=False)

    def get_issues_by_status(self, projectkey: str, status: str) -> List:
        """
        Retreive a List of Issues by its status.
        :param projectkey: The Project Key of the Jira Project.
        :param status: The status.
        :return: A list of Issues with the supplied status.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = {status} order by key", maxResults=False)

    def get_stories_of_user(self, projectkey: str, name: str) -> List:
        """
        Retreive a list of Issues that are assigned to a specific user.
        :param projectkey: The ProjectKey of the project.
        :param name: The name of the user.
        :return: A list of Issues that are assigned to the user.
        """
        user_id = self.jira.search_users(name)[0].accountId
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and assignee={user_id} order by key", maxResults=False)

    def get_stories_of_user_in_sprint(self, projectkey: str, name: str) -> List:
        """
        Retreive a list of Issues that are in the current Sprint and are assigned to a specific user.
        :param projectkey: The ProjectKey of the project.
        :param name: The name of the user.
        :return: A list of Issues that are in the current sprint and that are assigned to the user.
        """
        user_id = self.jira.search_users(name)[0].accountId
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and assignee={user_id} and sprint in openSprints() and sprint not in futureSprints() order by key", maxResults=False)

    def get_stories_of_user_in_backlog(self, projectkey: str, name: str) -> List:
        """
        Retreive a list of Issues that are in the current Backlog and are assigned to a specific user.
        :param projectkey: The ProjectKey of the project.
        :param name: The name of the user.
        :return: A list of Issues that are in the current Backlog and that are assigned to the user.
        """
        user_id = self.jira.search_users(name)[0].accountId
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and assignee={user_id} and sprint not in openSprints() and sprint not in futureSprints() order by key", maxResults=False)

    def get_components(self, projectkey: str) -> List:
        """
        Retrieve a list of all components of a Project in Jira.
        :param projectkey: The ProjectKey of the Project.
        :return: A list of components.
        """
        components = self.jira.project_components(projectkey)
        return components

    def get_component_by_name(self, projectkey: str, name: str) -> Any:
        """
        Retreive a Component Object by name
        :param projectkey: The ProjectKey of the Project.
        :param name: The name of the component.
        :return: A Component object.
        """
        component = [x for x in self.jira.project_components(projectkey) if x.name == name][0]
        return component

    def get_components_of_issue(self, issuekey: str) -> any:
        """
        Get all components of a specific Issue.
        :param issuekey: The IssueKey of the Issue to retreive the Components of.
        :return: A List of components that belong to the Issue.
        """
        issue = self.jira.issue(issuekey)
        return issue.fields.components

    def get_todo_in_sprint(self, projectkey: str) -> List:
        """
        Retreive a list of Issues in the current Sprint that have the status 'To Do'.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues with the status 'To Do'.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'To Do' and sprint in openSprints() and sprint not in futureSprints() order by key", maxResults=False)

    def get_done_in_sprint(self, projectkey: str) -> List:
        """
        Retreive a list of Issues in the current Sprint that have the status 'Done'.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues with the status 'Done'.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'Done' and sprint in openSprints() and sprint not in futureSprints() order by key", maxResults=False)

    def get_in_progress_in_sprint(self, projectkey: str) -> List:
        """
        Retreive a list of Issues in the current Sprint that have the status 'In progress'.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues with the status 'In progress'.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'In progress' and sprint in openSprints() and sprint not in futureSprints() order by key", maxResults=False)

    def get_closed_today_without_components(self, projectkey: str) -> List:
        """
        Retreive a list of Issues in the current Sprint that are closed today and have no components attached to it.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues in the current Sprint that are closed today and have no Components attached to it.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'Done' and sprint in openSprints() and sprint not in futureSprints() and updated >= startOfDay() and updated <= endOfDay() and components is EMPTY order by key", maxResults=False)

    def get_closed_without_components(self, projectkey: str) -> List:
        """
        Retreive a list of Issues in the that are closed and have no components attached to it.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues that are closed and have no Components attached to it.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'Done' and components is EMPTY order by key", maxResults=False)

    def get_closed_today_without_story_points(self, projectkey: str) -> List:
        """
        Retreive a list of Issues in the current Sprint that are closed today and have no Story Points.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues in the current Sprint that are closed today and have no Story Points.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'Done' and sprint in openSprints() and sprint not in futureSprints() and updated >= startOfDay() and updated <= endOfDay() and customfield_10004 is EMPTY order by key", maxResults=False)

    def get_all_issues_with_components(self, projectkey: str) -> List:
        """
        Retreive a list of Issues with their attached Components.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues with their attached Components.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and components is not EMPTY order by key", maxResults=False)

    def get_closed_today(self, projectkey: str) -> List:
        """
        Retreive a list of Issues that are closed (status 'Done') today.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues that are closed (status 'Done') today.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'Done' and sprint in openSprints() and sprint not in futureSprints() and updated >= startOfDay() and updated <= endOfDay() order by key", maxResults=False)

    def get_created_today(self, projectkey: str) -> List:
        """
        Retreive a list of Issues that are created (status 'to do') today.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Issues that are created (status 'to do') today.
        """
        return self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and status = 'To Do' and sprint in openSprints() and sprint not in futureSprints() and created >= startOfDay() and created <= endOfDay() order by key", maxResults=False)

    def get_email_addresses_of_all_assignees(self, projectkey: str) -> List:
        """
        Retreive a list of emailaddresses of all assignees for the given Issues.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of email addresses of assignees with their assigned IssueKeys.
        """
        issues = self.jira.search_issues(f"project={projectkey} and issuetype!=Epic and assignee is not EMPTY order by key", maxResults=False)
        assignees = []
        for issue in issues:
            assignees.append((issue.fields.assignee.emailAddress, issue.key))
        return assignees

    def report_statistics(self, projectkey: str) -> Any:
        """
        Create a Pandas DataFrame with report statistics from Jira.
        :param projectkey: The ProjectKey of the Project.
        :return: A Pandas DataFrame with report statistics.
        """
        openinsprint = len(self.get_issues_in_sprint(projectkey))
        inbacklog = len(self.get_issues_in_backlog(projectkey))
        nu = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y/%m/%d 00:00")
        closedlastweek = len(self.get_issues_by_jql(f"project={projectkey} and status changed to done after '{nu}'"))
        closedinsprint = len(self.get_issues_by_jql(f"project={projectkey} and sprint in openSprints() and issuetype!=Epic and status in (done) order by key"))
        todo = len(self.get_issues_by_jql(f"project={projectkey} and sprint in openSprints() and issuetype!=Epic and status in ('to do') order by key"))
        progress = len(self.get_issues_by_jql(f"project={projectkey} and sprint in openSprints() and issuetype!=Epic and status in ('in progress') order by key"))
        data = {'Sprint issues open': openinsprint, 'Sprint issues nog te doen': todo, 'Sprint issues in uitvoering': progress, 'Sprint issues afgesloten': closedinsprint, 'Issues in Backlog': inbacklog, 'Issues afgesloten in de laatste week': closedlastweek}
        return pd.Series(data).to_frame('Totaal')

    def report_statistics_per_component(self, projectkey: str) -> Any:
        """
        Create a Pandas DataFrame with report statistics per Component from Jira.
        :param projectkey: The ProjectKey of the Project.
        :return: A Pandas DataFrame with report statistics per Component.
        """
        comp = self.get_components(projectkey)
        df = pd.DataFrame(columns=['Component', 'Totaal', 'Open', 'In Sprint', 'Gesloten'])
        for i in range(len(comp)):
            c = comp[i]
            issuestotaal = self.get_issues_by_jql(f"project={projectkey} and component='{c['name']}' and issuetype!=Epic")
            issuesopen = self.get_issues_by_jql(f"project={projectkey} and component='{c['name']}' and issuetype!=Epic and status not in (done)")
            issuesclosed = self.get_issues_by_jql(f"project={projectkey} and component='{c['name']}' and issuetype!=Epic and status in (done)")
            insprint = self.get_issues_by_jql(f"project={projectkey} and sprint in openSprints() and issuetype!=Epic and component='{c['name']}' and status not in (done)")
            df.loc[i] = [c["name"], len(issuestotaal), len(issuesopen), len(insprint), len(issuesclosed)]
        return df

    def bug_does_exist(self, projectkey: str, summary: str) -> bool:
        """
        Check if a bug already exists in Jira.
        :param projectkey: The ProjectKey of the Project.
        :param summary: The summary of the Issue to check.
        :return: True if the Bug already exists in Jira, otherwise False.
        """
        ret = self.get_issues_by_status(projectkey, "to do")
        for i in ret:
            if str(i["fields"]["summary"]) == summary:
                return True
        return False

    def create_bug(self, projectkey: str, summary: str, description: str, componentname: str, sprintid: str) -> any:
        """
        Create a Bug in Jira.
        :param projectkey: The ProjectKey of the Project.
        :param summary: The summary of the Bug to create.
        :param description: The description of the Bug to create.
        :param componentname: The componentname of the Bug to create.
        :param sprintid: The SprintID of the Sprint in which to create the Bug.
        :return: The issue object.
        """
        issue = self.jira.create_issue(project=projectkey, summary=summary, description=description, issuetype={'name': 'Bug'}, components=[{'name': componentname}], customfield_10006=sprintid)
        return issue

    def get_initial_story_points(self, issuekey: str) -> int:
        """
        Retreive the original/initial Story Points that were assigned to an Issue.
        :param issuekey: The IssueKey of the Issue.
        :return: The original/initial Story Points that were assigned to an Issue
        """
        # /jira/rest/api/2/issue/DRW-124?expand=changelog
        url = f"{self.rooturl}/rest/api/2/issue/{issuekey}?expand=changelog"
        json_result = requests.get(url, verify=True, auth=(self.jira_user, self.jira_pwd))
        hist = json.loads(json_result.content)
        tmp = []
        for rw in hist["changelog"]["histories"]:
            dt = parser.parse(rw["created"])
            items = rw["items"]
            for i in items:
                if i["field"] == "Story Points":
                    tmp.append([dt, i["fromString"], i["toString"]])
        srt = sorted(tmp, key=lambda x: x[0])
        first = srt[0]
        return first[1]

    def get_all_issues(self, projectkey: str) -> List:
        """
        Retreive all Issues of a Project in Jira.
        :param projectkey: The ProjectKey of the Project.
        :return: A list of all Issues of the Project.
        """
        print(f"Retreiving all issues...")
        issues = self.jira.search_issues(f"project={projectkey} and issuetype!=Epic", maxResults=False)
        return issues

    def set_no_epic(self, keys: List):
        """
        Remove the Epic (set to None) for a list of Issues.
        :param keys:List of IssueKeys.
        """
        for key in keys:
            s_data = {"fields": {"customfield_10100": None}}
            url = f"{self.rooturl}/rest/api/2/issue/{key}"
            requests.put(url, verify=True, json=s_data, auth=(self.jira_user, self.jira_pwd))
            # issue_.update(issue_dict)
            print(f"Issue {key} updated to no epic.")

    def get_component_names(self, projectkey: str) -> List:
        """
        Retreive a List of Component names for a Project in Jira.
        :param projectkey: The ProjectKey of the Project.
        :return: A List of Component names.
        """
        components_ = self.get_all_issues_with_components(projectkey)
        components = []
        for c in components_:
            components.append(c["fields"]["components"][0]["name"])
        return list(set(components))

    def create_new_project(self, projectname: str, projectkey: str, template: str = "SCRUM"):
        """
        Create a new Project in Jira.
        :param projectname: The name of the Project to create.
        :param projectkey: The ProjectKey of the Project to create.
        :param template: The template to use for the Project to create (SCRUM or KANBAN).
        """
        try:
            self.jira.create_project(name=projectname, key=projectkey, template_name=template, ptype="software")
        except Exception as e:
            pass
