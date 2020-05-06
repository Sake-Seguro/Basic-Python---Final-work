###### The final work on Python basics
###### The very description of the task  for this work is placed within README.md

import requests
from urllib.parse import urlencode
import time
import json
from pprint import pprint
from termcolor import colored


####### The algorithm of our actions to be as follows: 
####### To create a concrete function for each set of activities cited below
####### 1) Getting VK_user_id or transmuting it into a suitable form;
####### 2) Acquiring the list of his/ her groups of interest;
####### 3) Receiving the list of his/ her friends;
####### 4) Taking for comparison the list of his/ her friends' interests;
####### 5) Writing adequate data into a json_file.

TOKEN = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'


def target_vk_user():
    
    """
    Entering the data of a particular VK-user for our analysis
    
    """
    
    vk_user_id = input('\nEnter any VK-user by name or by his/ her ID in this social network and press enter to start a comparative analysis: ')
    
    try:
        int(vk_user_id)
        print(colored(f'\nFor making a comparative analysis the system will use the data of a VK-user # {vk_user_id}.', 'blue'))
        return int(vk_user_id)
    
    except ValueError:
        if vk_user_id == "":
            print(colored('\nSince you did not enter either ID or the name of a VK-user the system will use the data provided by default, i.e. 171691064/ eshmargunov', 'blue'))
            return 171691064
        else:
            print(colored(f'\nThe comparative analysis will be executed in relation to the VK-user {vk_user_id}.', 'blue'))
            letter_user_id = transmuting_into_numeric_id(vk_user_id)
            return int(letter_user_id)


def transmuting_into_numeric_id(vk_user_id):
    
    """
    If a VK-user's data was not entered for a comparative analysis by his/ her numeric ID the system will acquire it through the API.

    """

    params = {
        'access_token': TOKEN,
        'user_ids': vk_user_id,
        'v': 5.103
    }
    response = requests.get(
        'https://api.vk.com/method/users.get',
        params
    )
    response_json = response.json()
    letter_user_id = response_json['response'][0]['id']

    print(colored(f'The result of the data transmuting is {letter_user_id}.', 'blue'))
    return int(letter_user_id)


def personal_interest_groups(vk_user_id):
    
    """
    Requesting groups of interests of the VK-user under analysis at this stage

    """

    params = {
        'access_token': TOKEN,
        'user_id': vk_user_id,
        'v': 5.103,
        'extended': 1,
        'count': 1000
    }
    response = requests.get(
        'https://api.vk.com/method/groups.get',
        params
    )
    response_json = response.json()
    
    vkuser_interest_groups = set()
    
    if response_json.get('error') and (response_json['error']['error_msg'] == 'This profile is private' or \
                                       response_json['error']['error_msg'] == 'User was deleted or banned'):
        print(colored(f'\n\nThe system cannot look through the groups of the friend with ID {vk_user_id} '
              f"due to the error cited as {response_json['error']['error_msg']}.", 'red', 'on_white'))
        return vkuser_interest_groups
    
    elif response_json.get('error') and (response_json['error']['error_msg'] == 'Too many requests per second'):
        print(colored(f"\nIt's necessary to wait for some seconds because of the error {response_json['error']['error_msg'] }.", 'green'))
        time.sleep(1.1)
        response_json = response.json()
    
    print(f'\nThe system is searching for groups of the VK-user with an ID {vk_user_id}: ')
    
    try:
        for group in response_json['response']['items']:
            print(".", end="")
            vkuser_interest_groups.add(group['id'])
        return vkuser_interest_groups
    except:
        return vkuser_interest_groups


def determining_friends(vk_user_id):
    
    """
    Retrieving the list of targeted friends, VK-users
    
    """

    params = {
        'access_token': TOKEN,
        'user_id': vk_user_id,
        'v': 5.103
    }
    response = requests.get(
        'https://api.vk.com/method/friends.get',
        params
    )
    response_json = response.json()
    
    if response_json.get('error') and (response_json['error']['error_msg'] == 'Too many requests per second'):
        print(colored(f"\nIt is necessary to wait for some seconds because of the error {response_json['error']['error_msg']}.", 'green'))
        time.sleep(1.2)
        response_json = response.json()
    
    targeted_vkuser_friends = list()
    
    print(f'\nSearching for friends of the VK-user under this comparative analysis {vk_user_id}: ')
    
    for friend in response_json['response']['items']:
        print(".", end = "")
        targeted_vkuser_friends.append(friend)
    return targeted_vkuser_friends


def comparing_interest_groups(initial_group, targeted_genuine_friends):
    
    """
    Transferring the list of genuine groups and friends;
    Receiving the list of interest groups for each friend to compare them with a genuine one

    """

    processed_groups = initial_group
    
    for friend in targeted_genuine_friends:
        vkuser_interest_groups = personal_interest_groups(friend)
        unified_groups = processed_groups.difference(vkuser_interest_groups)
        processed_groups = unified_groups
    return processed_groups


def providing_group_details(correlated_vkgroups):
    
    """
    Providing details of groups under comparison

    """

    print(colored(f'\n\nTotally we received - {len(correlated_vkgroups)} unique group(-s) with the following attributes: {correlated_vkgroups}.\n', 'blue'))
    
    target_unique_list = []
    
    for vkgroup in correlated_vkgroups:
        params = {
            'access_token': TOKEN,
            'v': 5.103,
            'group_id': vkgroup,
            'fields': "name,members_count"
        }
        response = requests.get(
            'https://api.vk.com/method/groups.getById',
            params
        )
        response_json = response.json()
        
        if response_json.get('error') and (response_json['error']['error_msg'] == 'Too many requests per second'):
            print(colored(f"\nIt is necessary to wait for some seconds due to the error {response_json['error']['error_msg']}.", 'green'))
            time.sleep(1.3)
            response_json = response.json()
        for target_group in response_json['response']:
            designated_dict = {}
            designated_dict = {'name': target_group['name'], 'gid': target_group['id'], 'members_count': target_group['members_count']}
            target_unique_list.append(designated_dict.copy())
    return target_unique_list


def main():
    
    initial_vkuser = target_vk_user()
    initial_group = personal_interest_groups(initial_vkuser)
    targeted_genuine_friends = determining_friends(initial_vkuser)
    correlated_dataset = comparing_interest_groups(initial_group, targeted_genuine_friends)
    final_results_json = providing_group_details(correlated_dataset)
    
    ############ To check the readiness of the very file we could use pprint
    #pprint(final_results_json)
    
    with open('groups.json', 'w', encoding='utf-8') as target_file:
        json.dump(final_results_json, target_file, indent=3, ensure_ascii=False)
    
    return print(colored('\nOur analysis was realized successfully.\nThe file groups.json is prepared accordingly.', 'blue'))


if __name__ == "__main__":

  main()





