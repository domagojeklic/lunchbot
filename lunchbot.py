import os
import time
import re
import textwrap
import persistance
from orders import *
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
CHAT_POST_MESSAGE = 'chat.postMessage'
REACTION_ADD = 'reactions.add'

CMD_ORDER_REGEX = 'order\s+(.*)\s+from\s+(\S+)'
CMD_ORDER_MEAL_PRICE_REGEX = '^(.*?)([0-9]+(?:,|.)?[0-9]*)\s*(?:kn?)?$'

CMD_NOTIFY_REGEX = '^notify\s+(\S+)\s*(.+)?$'

CMD_DISCOUNT_REGEX = '^discount\s+(\S+)\s(\d+)\s*%$'

orders = Orders()

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["ts"], event["channel"], event["user"]
    return None, None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(channel, timestamp, from_user, command):
    """
        Executes bot command if the command is known
    """

    matches = re.search(CMD_ORDER_REGEX, command)
    if matches:
        meal_price = matches.group(1).strip()
        restaurant = matches.group(2).strip()
        
        matches_mp = re.search(CMD_ORDER_MEAL_PRICE_REGEX, meal_price)
        if matches_mp:
            meal = matches_mp.group(1).strip()
            price = float(matches_mp.group(2).strip().replace(',', '.'))

            print('Order received:\nRestaurant: {0}\nMeal: {1}\nPrice: {2}\n'.format(restaurant, meal, price))

            handle_order(channel, timestamp, from_user, meal, price, restaurant)
            return

    matches = re.search(CMD_NOTIFY_REGEX, command)
    if matches:
        restaurant = matches.group(1)
        message = matches.group(2)

        notify_restaurant(channel, restaurant, message)
        return
    
    matches = re.search(CMD_DISCOUNT_REGEX, command)
    if matches:
        restaurant = matches.group(1)
        percentage = int(matches.group(2))
        discount_restaurant(channel, restaurant, percentage)
        return

    command_arr = command.split()
    command_arr_len = len(command_arr)
    command = command_arr[0]

    if (command_arr_len == 1 or command_arr_len == 2) and command == 'summarize':
        restaurant = command_arr[1] if command_arr_len > 1 else None
        if restaurant == 'all':
            summarize_all_restaurants(channel)
        else:
            summarize_restaurant(channel, restaurant)
        return

    if command_arr_len == 2 and command == 'clear' and command_arr[1] == 'all':
        clear_all_restaurants(channel)
        return
    
    if command_arr_len == 2 and command == 'clear':
        clear_restaurant(channel, command_arr[1])
        return

    if command_arr_len == 3 and command == 'cancel' and command_arr[1] == 'my' and command_arr[2] == 'orders':
        cancel_orders(channel, from_user)
        return
    
    if command_arr_len == 1 and command == 'help':
        print_usage(channel)
        return

    # Sends the response back to the channel
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='<@{0}> not sure what you mean. Try typing *help* to get the list of supported commands!'.format(from_user)
    )

#Helpers

def usage_description():
    return textwrap.dedent("""
        *Commands* and _arguments_ :fork_and_knife:\n
        *order* _meal_ *from* _restaurant_
        \t• Order meal from restaurant
        *summarize* _restaurant_
        \t• Summarize all orders from restaurant
        *summarize all*
        \t• Summarize orders from all restaurants
        *notify* _restaurant_ _message_
        \t• Send _message_ to all users from restaurant
        *cancel my orders*
        \t • Cancel orders from user
        *clear* _restaurant_
        \t• Clear all orders from restaurant
        *clear all*
        \t• Clear all orders
        """)

#Custom defined commands

def handle_order(channel, timestamp, from_user, meal, price, restaurant):
    orders.add_order(restaurant, meal, price, from_user)

    persistance.save_orders(orders)

    slack_client.api_call(
        REACTION_ADD,
        channel=channel,
        timestamp=timestamp,
        name="white_check_mark"
    )

def summarize_restaurant(channel, restaurant):
    summarized = orders.summarize(restaurant)
    
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=summarized
    )

def summarize_all_restaurants(channel):
    summarized = orders.summarize_all()

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=summarized
    )

def notify_restaurant(channel, restaurant, message):
    final_message = orders.notify_restaurant(restaurant, message)

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=final_message
    )

def discount_restaurant(channel, restaurant, percentage):
    message = orders.apply_discount(restaurant, percentage)

    persistance.save_orders(orders)

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=message
    )

def cancel_orders(channel, from_user):
    orders.cancel_orders(from_user)
    
    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='Canceled all orders from <@{0}>'.format(from_user)
    )


def clear_restaurant(channel, restaurant):
    message = orders.clear_restaurant(restaurant)

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=message
    )

def clear_all_restaurants(channel):
    orders.clear_all()

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text='All orders cleared'
    )

def print_usage(channel):

    slack_client.api_call(
        CHAT_POST_MESSAGE,
        channel=channel,
        text=usage_description()
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        orders = persistance.load_orders()
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, timestamp, channel, from_user = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(channel, timestamp, from_user, command)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
