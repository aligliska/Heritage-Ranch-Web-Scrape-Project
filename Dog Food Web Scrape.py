from bs4 import BeautifulSoup
import requests
from os import listdir, getcwd
from os.path import isfile, join
import re

'''
Initial attempt to webscrape HEB Site for dog food analysis based on input html link.
Eventually got blocked from pull requests after a few attempts. Overall, manual
html parsing methods could have been applied to webscraped data if access to the
information had not been blocked. 
'''
def get_ingredients_HEB(url):
    # request to scrape the url 
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    # find the title specific element (manually determined for ingredients)
    ## need to verify this is consistent for all HEB type websites for dog food
    find_elements = doc.find_all("p")
    ingredients = str(find_elements[1])
    ingredients = ingredients.split(sep = "\n")[-1]
    ingredients = ingredients.split(sep = ".")[0]
    ingredients = ingredients.split(sep = ", ")
    ingredients = [item.strip() for item in ingredients]

    # print out the list of ingredients
    for item in ingredients:
        if item.lower() == "salt":
            print()
            print("1% Demarketer")
            print()
        print(item)

    return


## Alternative method if web scrapping access is blocked

def HR_Get_Ingredients(onlyfiles):
    '''
    Returns a list of ingredients for particular food. Access options from initial list of available
    dry food options. (Based on the format on the HEB website)
    '''
    # selects which dry food to analyze
    option = int(input("Which Heritage Dry Kibble would you like to analyze? Enter the index number.\n"))
    file = onlyfiles[option]

    # removes extraneous tags on the name of dry food 
    name = file.rstrip("- Shop Dogs at H-E-B.html")
    name = name[24:].strip()

    # opens and reads the html file for the specified dry food 
    with open(file, "r") as f:
        doc = BeautifulSoup(f, "html.parser")

        # search for ingredients using html indicators 
        find_elements = doc.find_all("p")
        ingredients = str(find_elements[1])
        ingredients = ingredients.split(sep = "\n")[-1]
        ingredients = ingredients.split(sep = ".")[0]
        ingredients = ingredients.split(sep = ", ")

        # clean ingredient names
        ingredients = [item.strip() for item in ingredients]
        for i in range(len(ingredients)):
            if ingredients[i][:10] == "Vitamins (":
                ingredients[i] = ingredients[i][10:]
                continue
            elif ingredients[i][-1] == ")" and "(" not in ingredients[i]:
                ingredients[i] = ingredients[i][:-1]
                continue
            elif ingredients[i][:10] == "Minerals (":
                ingredients[i] = ingredients[i][10:]
                continue
        
    return name, ingredients

def HR_Get_Ratios(onlyfiles):
    '''
    Returns a list of the percentages from the guaranteed analysis. 
    '''
    # selects which dry food to analyze
    option = int(input("Which Heritage Dry Kibble would you like to analyze? Enter the index number.\n"))
    file = onlyfiles[option]

    # removes extraneous tags on the name of dry food 
    name = file.rstrip("- Shop Dogs at H-E-B.html")
    name = name[24:].strip()

    # opens and reads the html file for the specified dry food 
    with open(file, "r") as f:
        doc = BeautifulSoup(f, "html.parser")

        # search for the guaranteed analysis using html indicators and keyword search  
        find_elements = doc.find_all("p")
        analysis = str(find_elements[1])
        start = analysis.find("Guaranteed Analysis:")
        analysis = analysis[start:].strip("</p>").strip("Guaranteed Analysis: ")
        analysis = analysis.split(sep = ",")
        analysis = [item.strip() for item in analysis]
        
    return name, analysis

def HR_Get_Calories(onlyfiles):
    '''
    Returns the calories per kg and calories per cup of indicated dry food.
    '''
    # selects which dry food to analyze
    option = int(input("Which Heritage Dry Kibble would you like to analyze? Enter the index number.\n"))
    file = onlyfiles[option]

    # removes extraneous tags on the name of dry food 
    name = file.rstrip("- Shop Dogs at H-E-B.html")
    name = name[24:].strip()

    # opens and reads the html file for the specified dry food 
    with open(file, "r") as f:
        doc = BeautifulSoup(f, "html.parser")
        
        #  search for the calorie content using html indicators and keyword search  
        find_elements = doc.find_all(class_ = "pdp-product-desc__text-content")
        calories = str(find_elements[1])
        start = calories.find("Calorie Content")

        # extracts numerical content from string of characters
        calories = calories[start:start + 50].replace(",", "")
        calories = re.sub("[^0-9]", "", calories)

        # extracts calories per kg and calories per cup 
        cal_per_kg = calories[:4]
        cal_per_cup = calories[4:]

    return name, cal_per_kg, cal_per_cup
        
def HR_Portion_Size(onlyfiles):
    '''
    Determines the recommended daily amount of dry food to feed user's dog based on calorie content of
    specified food and the dog's background. 
    '''
    # gets the calories per cup for the specified dry food 
    name, cal_per_kg, cal_per_cup = HR_Get_Calories(onlyfiles)
    cal_per_cup = int(cal_per_cup)

    # weight input in pounds for USA convenience; converted to kg for calculations 
    weight = float(input("Enter your dog's weight in pounds (lbs): "))* 0.453592
    print()
    
    # number of calories the dog needs to eat per day --> RER
    RER = 70 * weight**(3/4)

    # collect background information for the dog to determine amount of dry food
    activity_level = ["Low", "Moderate", "High"]
    possible_ages = ["Puppy", "Adult", "Senior"]
    altered_state = ["Neutered/Spayed", "Intact"]
    
    for e, state in enumerate(activity_level):
        print(f"({e}) {state}")
    activity_state = int(input("How active is your dog? Enter the corresponding index value: "))
    print()
    
    for e, age in enumerate(possible_ages):
        print(f"{(e)} {age}")
    age_of_dog = int(input("What lifestage is your dog in? Enter the corresponding index value: "))
    print()
    
    if age_of_dog == 0:
        print("(0) Puppy 0-4 months")
        print("(1) Puppy 4+ months to yound adult")
        age_puppy = int(input("How old is your puppy? Enter the corresponding index value: ")) 
    print()
    
    for e, state in enumerate(altered_state):
        print(f"({e}) {state}")
    altered_dog = int(input("Is your dog neutered/spayed? Enter the corresponding index value: "))
    print()
    
    # get RER multiplier for lowly active and inactive dogs
    if activity_level != 2:
        # adult dog 
        if age_of_dog == 1:
            # moderate activity dogs
            if altered_dog == 0 and activity_state == 1:
                multiplier = 1.6
            elif altered_dog == 1 and activity_state == 1:
                multipler = 1.8
            # inactive/low activity dogs
            elif altered_dog == 0 and activity_state == 0:
                multiplier = 1.3
            elif altered_dog == 1 and activity_state == 0:
                multipler = 1.4

        # senior dog; assuming low activity levels due to age constraint 
        elif age_of_dog == 2:
            multiplier = 1.2

        # puppy dog
        elif age_of_dog == 0:
            if age_puppy == 0:
                multiplier = 3.0
            elif age_puppy == 1:
                multiplier = 2.0

        # calculates the recommended daily amount of dry food  
        amount = RER * multiplier / cal_per_cup
        amount = round(amount, 2)

    # active dogs --> generate range; varies depending on activity level
    else:
        lower_multiplier = 2.0
        upper_multiplier = 5.0

        lower_amount = RER * lower_multiplier / cal_per_cup
        lower_amount = round(lower_amount, 2) 
        upper_amount = RER * upper_multiplier / cal_per_cup
        upper_amount = round(upper_amount, 2) 

        amount = str(lower_amount) + " - " + str(upper_amount)
    
    return name, amount

def HR_Get_All_Calories(onlyfiles):
    '''
    Returns all calories per cup for all available dry food. Sorts list into ascending order. 
    '''
    store_calories = []
    names = []
    # loop through all dry food options 
    for i in range(len(onlyfiles)):
        file = onlyfiles[i]
        name = file.rstrip("- Shop Dogs at H-E-B.html")
        name = name[24:].strip()

        # opens each html file and extracts the calories per cup 
        with open(file, "r") as f:
            doc = BeautifulSoup(f, "html.parser")
            find_elements = doc.find_all(class_ = "pdp-product-desc__text-content")
            calories = str(find_elements[1])
            start = calories.find("Calorie Content")
            calories = calories[start:start + 50].replace(",", "")
            calories = re.sub("[^0-9]", "", calories)
            cal_per_cup = calories[4:]
        
        store_calories.append(cal_per_cup)

        # removes extraneous tags from name 
        name = onlyfiles[i].rstrip("- Shop Dogs at H-E-B.html")
        name = name[24:].strip()
        names.append(name)

    # creates a dictionary for the calorie content and respective dry food 
    calorie_dict = dict(zip(names, store_calories))

    sorted_calorie_dict = sorted(calorie_dict.items(), key =lambda x: x[1])
    return sorted_calorie_dict

def HR_Find_Controversial(onlyfiles):
    '''
    Identifies if there are dangerous or controversial ingredients in the specific dry food. 
    '''
    # gets the ingredients list for the specified dry food 
    name, ingredients = HR_Get_Ingredients(onlyfiles)
    ingredients = set(ingredients)

    # opens and reads controverial ingredients file (manually compiled into a .rtf file) 
    file = "Controversial_Ingredients.rtf"
    with open(file, "r") as f:
        in_file = f.readlines()[7:]
        in_file[0] = in_file[0].strip("\f0\fs24 \cf0 ")
        in_file = [line.strip("\\\n").strip("}").strip() for line in in_file]
        in_file = set(in_file)

    # determines if there are overlap in the two sets 
    c_ingredients = in_file.intersection(ingredients)
    
    return name, c_ingredients

def HR_Compare_PFF(onlyfiles):
    '''
    Returns all protein, fat, and fiber percentages for all available dry food.
    '''
    names, protein, fat, fiber = [], [], [], []

    # loops through all dry food options 
    for i in range(len(onlyfiles)):
        file = onlyfiles[i]
        name = file.rstrip("- Shop Dogs at H-E-B.html")
        name = name[24:].strip()
        names.append(name)

        # opens and reads each html file and extracts the three percentages
        with open(file, "r") as f:
            doc = BeautifulSoup(f, "html.parser")
            find_elements = doc.find_all("p")

            # search for ratios 
            analysis = str(find_elements[1])
            start = analysis.find("Guaranteed Analysis:")
            analysis = analysis[start:].strip("</p>").strip("Guaranteed Analysis: ")
            analysis = analysis.split(sep = ",")
            analysis = [item.strip() for item in analysis]

        # isolates the percentages
        protein.append(analysis[0].strip("Crude").replace("Protein: Min. (", "").strip(")"))
        fat.append(analysis[1].strip("Crude").replace("Fat: Min. (", "").strip(")"))
        ## Note: there was a typo in the original site description --> should have all been fiber
        fiber.append(analysis[2].strip("Crude").replace("Fiber: Max. (", "").replace("Fat: Max. (", "").strip(")"))

    return names, protein, fat, fiber

def main2():
    '''
    Navigation method to continuously use the functions in this project until user quits.
    '''
    mypath = getcwd()
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles.remove(".DS_Store")
    onlyfiles.remove("Dog Food Web Scrape.py")
    onlyfiles.remove("Controversial_Ingredients.rtf")
    
    status = True

    menu = ["Full Ingredients List", "Top Ingredients List", "Supplemental Ingredients List",
            "Guaranteed Analysis", "Individual Calorie Content", "Amount to Feed per Day",
            "All Heritage Ranch Dry Kibble Calorie Content", "Controversial Ingredients",
            "Protein/Fat/Fiber All comparison"]

    while status == True:
        print("Heritage Ranch Dry Food Options:")
        for num, file in enumerate(onlyfiles):
            file = file.rstrip("- Shop Dogs at H-E-B.html")
            file = file[24:].strip()
            print(f"({num}) {file}")
        print()
        
        print("What would you like to do? Enter the index number.")
        for e, m in enumerate(menu):
            print(f"({e}) {m}")
        print()
        print("Enter 'quit' if you would like to exit")
        choice = input()
        print()

        # returns full ingredients list w/ 1% demarketer 
        if choice == str(0):
            name, ingredients = HR_Get_Ingredients(onlyfiles)

            print(f"{menu[int(choice)]} for {name}:")
            for i in range(len(ingredients)):
                if ingredients[i] == "Salt":
                    print()
                    print("1% Demarketer")
                    print()
                print(ingredients[i])
            print()

        # returns  ingredients with higher than 1% concentration
        elif choice == str(1):
            name, ingredients = HR_Get_Ingredients(onlyfiles)
            print(f"Ingredients higher than 1% concentration for {name}:")
            end = int(ingredients.index("Salt"))
            for i in range(end):
                print(ingredients[i])
            print()
            print(f"There are {end} ingredients with concentrations > 1%.")
            print()

        # returns ingredients with less than 1% concentration 
        elif choice == str(2):
            name, ingredients = HR_Get_Ingredients(onlyfiles)
            print(f"Ingredients ≤ 1% concentration for {name}:")
            start = int(ingredients.index("Salt"))
            # only print ingredients after salt 
            for i in range(start, len(ingredients)):
                print(ingredients[i])
            print()
            print(f"There are {len(ingredients) - start} ingredients with concentrations ≤ 1%.")
            print()

        # returns the percentages from the guaranteed analysis
        elif choice == str(3):
            name, analysis = HR_Get_Ratios(onlyfiles)
            print(f"The {menu[int(choice)]} for {name}:")
            for item in analysis:
                print(item)
            print()

        # returns the calorie content 
        elif choice == str(4):
            name, cal_per_kg, cal_per_cup = HR_Get_Calories(onlyfiles)
            print(f"{menu[int(choice)]}:")
            print(f"kcal per kilogram: {cal_per_kg}.")
            print(f"kcal per cup: {cal_per_cup}.")
            print()

        # returns the recommended daily portion size
        elif choice == str(5):
            name, amount = HR_Portion_Size(onlyfiles)
            print(f"Based on your dog's background, the recommended amount of {name} is {amount} cups daily.")
            print()

        # returns all the calories for the dry food options in ascending order
        elif choice == str(6):
            calorie_dict = HR_Get_All_Calories(onlyfiles)
            print("Kcal per Cup | Type of Kibble")
            for entry in calorie_dict:
                print(f"{int(entry[1])} | {entry[0]}")
            print()

        # returns controversial ingredients used in the dry food 
        elif choice == str(7):
            name, c_ingredients = HR_Find_Controversial(onlyfiles)
            print(f"{menu[int(choice)]} for {name}:")
            if len(c_ingredients) == 0:
                print("Not Detected!")
            else:
                for item in c_ingredients:
                    print(item)
            print()

        # returns all the protein, fat, fiber guaranteed analysis for the dry food options
        elif choice == str(8):
            names, protein, fat, fiber = HR_Compare_PFF(onlyfiles)
            print("Protein% | Fat% | Fiber% | Name")
            for i in range(len(protein)):
                print(f"{protein[i].center(8)} |{fat[i].center(5)} |{fiber[i].center(7)} |{names[i]}")
            print()

        # exits the program
        elif choice.lower() == "quit":
            print("Good bye!")
            status = False
        
    return

main2()







