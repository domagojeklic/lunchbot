class Meal:
    '''
        Holds information about individual meal orders
    '''
    def __init__(self, name: str, price: float, user: str):
        self.name = name
        self.price = price
        self.users = [user]

    def add_user(self, user: str):
        self.users.append(user)

    def total_number(self) -> int:
        return len(self.users)

    def total_price(self) -> float:
        return self.total_number() * self.price

class Restaurant:
    '''
        Holds information about orders from individual restaurant
    '''
    def __init__(self, name):
        self.name = name
        self.meals_dict = {}

    def add_meal(self, meal: Meal):
        self.meals_dict[meal.name] = meal

    def add_order(self, meal_name: str, meal_price: float, from_user: str):
        if meal_name in self.meals_dict:
            meal = self.meals_dict[meal_name]
            meal.add_user(from_user)
        else:
            meal = Meal(meal_name, meal_price, from_user)
            self.add_meal(meal)
    
    def summarize(self) -> str:
        totalPrice = 0

        summarized = '*{0}:*\n'.format(self.name)
        for meal_name, meal in self.meals_dict.items():
            totalPrice += meal.total_price()
            summarized += '_{0}_, *{1}kn* x{2}'.format(meal_name, meal.total_price(), meal.total_number())
            summarized += ' ('
            for i in range(len(meal.users)):
                u = meal.users[i]
                summarized += '<@{0}>'.format(u)
                if not i == len(meal.users) - 1:
                    summarized += ', '
            summarized += ')\n'
        
        summarized += '\n_Total:_ *{0}kn*'.format(totalPrice)

        return summarized

class Orders:
    '''
        Holds information about orders from all restaurants
    '''
    def __init__(self):
        self.restaurants_dict = {}

    def add_order(self, restaurant_name: str, meal_name: str, meal_price :float, from_user: str):
        rest_name_lower = restaurant_name.lower()
        if rest_name_lower in self.restaurants_dict:
            restaurant = self.restaurants_dict[rest_name_lower]
            restaurant.add_order(meal_name, meal_price, from_user)
        else:
            restaurant = Restaurant(rest_name_lower)
            restaurant.add_order(meal_name, meal_price, from_user)
            self.restaurants_dict[rest_name_lower] = restaurant

    def clear_all(self):
        '''
            Clears all orders from every restaurant
        '''
        self.restaurants_dict.clear()

    def clear_restaurant(self, restaurant_name) -> str:
        '''
            Clears all orders from restaurant
        '''
        rest_name_lower = restaurant_name.lower()
        if rest_name_lower in self.restaurants_dict.keys():
            del self.restaurants_dict[rest_name_lower]
            return 'All orders from *{0}* cleared!'.format(restaurant_name)
        else:
            return 'There are no orders from *{0}*'.format(restaurant_name)

    def cancel_orders(self, from_user: str):
        '''
            Clears all orders from a particular user
        '''
        delete_restaurants = []
        for restaurant_name, restaurant in self.restaurants_dict.items():
            delete_meals = []
            for meal_name, meal in restaurant.meals_dict.items():
                if from_user in meal.users:
                    meal.users.remove(from_user)
                if len(meal.users) == 0:
                    delete_meals.append(meal_name)
            
            for meal_name in delete_meals:
                del restaurant.meals_dict[meal_name]
            
            if len(restaurant.meals_dict) == 0:
                delete_restaurants.append(restaurant_name)
        
        for restaurant_name in delete_restaurants:
            del self.restaurants_dict[restaurant_name]
    
    def summarize(self, restaurant_name: str) -> str:
        '''
            Returns formated description of all orders from restaurant
        '''
        if restaurant_name == None:
            return 'Please specify restaurant name or *summarize all* for all restaurants'
        elif restaurant_name in self.restaurants_dict:
            restaurant = self.restaurants_dict[restaurant_name]
            return restaurant.summarize()
        else:
            return 'There are no orders from *{0}*'.format(restaurant_name)

    def summarize_all(self) -> str:
        '''
            Returns formated description of all orders from all restaurants
        '''
        summarized = ''
        for restaurant in self.restaurants_dict.values():
            summarized += restaurant.summarize()
            summarized += '\n-----------------------------------------------------\n'
        
        return summarized if len(summarized) > 0 else 'There are no orders'

