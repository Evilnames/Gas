import random, datetime, math

# Internal game counters
gasOwned        = 1000
gasEarnedInGame = 0
gasUsedInGame   = 0
tankersCaptured = 0
totalBreakdowns = 0
carList = []

# Various tankers could be moving about the wasteland, a modern max size is 11.5kg
gasPerTanker = [1000, 2500, 3500, 5500, 6500, 9000, 11500]
carsOwned = 10

# Range of how many cars go out to scout each day
minCarsToSendOnHunt = 2
maxCarsToSendOnHunt = 5

# How many miles do we want to drive per day to find a tanker.
minMilesDrivePerDay  = 10
maxMilesDrivePerDay = 45


# How often do we expect to find a disabled or damaged vehicle that we can tow back to base.
chanceOfFindingVehicleOnScout = 1

# Chance of finding a tank while out on hunt
chanceToGetTanker = 1

daysToSimulate = 365


#https://madmax.fandom.com/wiki/Category:Vehicles
carTypes = [
                {'type':'Pickup Truck', 'mpg':15,   'maxCrew': 4,   'chanceOfDestroy':5,    'breakDownRisk':10, 'breakDownRiskCombat':20,   'maxDaysToFix':7},
                {'type':'Buggy',        'mpg':25,   'maxCrew':4,    'chanceOfDestroy':3,    'breakDownRisk':5,  'breakDownRiskCombat':4,    'maxDaysToFix':4},
                {'type':'War Rig',      'mpg':15,   'maxCrew':25,   'chanceOfDestroy':2,    'breakDownRisk':35, 'breakDownRiskCombat':10,   'maxDaysToFix':35},
                {'type':'Bus',          'mpg':10, 'maxCrew':15,     'chanceOfDestroy':1,    'breakDownRisk':20, 'breakDownRiskCombat':10,   'maxDaysToFix':20},
                # Based on the Ford Inceterceptor from Original Mad Max
                {'type':'Interceptor',  'mpg':30,   'maxCrew':2,    'chanceOfDestroy':2,    'breakDownRisk':9,  'breakDownRiskCombat':12,   'maxDaysToFix':3},
                # Gyrocopter mostly a scout thing, getting into combat isn't useful
                {'type':'Gyrocopter',   'mpg':5,    'maxCrew':1,    'chanceOfDestroy':10,   'breakDownRisk':40, 'breakDownRiskCombat':25,   'maxDaysToFix':45},
            ]




# Used for most things in this simulation, testing against a 100% chance
def percentDieRoll(chance):
    roll = random.randrange(1,100)
    return chance >= roll

# How much gas is used when we go on a mission
def gasUsed(activeCars, minMiles, maxMiles):
    totalGasUsed = 0
    milesDrivenToday = random.randrange(minMiles, maxMiles)
    for car in activeCars:
        totalGasUsed += milesDrivenToday / car['mpg']

    return totalGasUsed

# Which type of tanker did we bag today?
def tankerResult(gasInATanker):
    capturedTanker = random.randrange(1, len(gasInATanker))
    return gasInATanker[capturedTanker]

# Get a list of cars going out on missions today
def getCarsOnMissionToday(cars, minCarsOnHunt, maxCarsOnHunt):
    # Figure out how many cars to send
    carsToSendOnHunt = random.randrange(minCarsOnHunt, maxCarsOnHunt)

    activeCars = list(filter(lambda car: car['status'] == 'Active', cars))
    if(carsToSendOnHunt > len(activeCars)):
        carsToSendOnHunt = len(activeCars)

    if(carsToSendOnHunt == 0):
        return []
    else:
        return random.sample(activeCars, k=carsToSendOnHunt)

# Process results for the day for each car
def dailyCarResults(cars, tankerResult, activeCars, totalBreakdowns):
    for car in cars:
        #Handle reduction in repair days
        if(car['status'] == 'Damaged'):
            if(car['repairDays'] == 0):
                car['status'] = 'Active'
            else:
                car['repairDays'] -= 1
            

        for active in activeCars:
            if(active['carId'] == car['carId']):
                if(tankerResult):
                    wasIDamaged = percentDieRoll(car['breakDownRiskCombat'])
                else:
                    wasIDamaged = percentDieRoll(car['breakDownRisk'])

                if(wasIDamaged):
                    totalBreakdowns = totalBreakdowns + 1
                    car['status'] = 'Damaged'
                    car['repairDays'] = random.randrange(1,car['maxDaysToFix'])
                    amIDead = percentDieRoll(car['chanceOfDestroy'])
                    if(amIDead):
                        car['status'] = 'Destroyed'
                
                car['missions'] = car['missions'] + 1
    return totalBreakdowns

# Some stats for output
def carInventoryStatus(carList):
    statusCount = {'Active':0, 'Damaged':0, 'Destroyed':0, 'TotalCars':0}
    statusCount['TotalCars'] = len(carList)

    for car in carList:
        statusCount[car['status']] += 1

    return statusCount

# Display stats collected
def printCarStatus(stats):
    print("Active:{Active} \t\t Damaged:{Damaged} \t\t Destroyed:{Destroyed}".format(Active=stats['Active'], Damaged=stats['Damaged'], Destroyed=stats['Destroyed']))

# Print out inventory of cars
def printCarDisplay(carList):
    print("CarId \t\t Status \t\t Missions \t\t Type")
    for car in carList:
        print("{id} \t\t {status} \t\t {missions} \t\t {carType}".format(id=car['carId'], status=car['status'], missions=car['missions'], carType = car['type']))

def newVehicle(carId, startStatus, startRepairDays, carType):
    return {'carId':carId, 'status':startStatus, 'missions':0, 'repairDays' : startRepairDays, 'type':carType['type'], 'mpg':carType['mpg'], 'maxCrew':carType['maxCrew'], 'chanceOfDestroy':carType['chanceOfDestroy'], 'breakDownRisk':carType['breakDownRisk'], 'breakDownRiskCombat':carType['breakDownRiskCombat'], 'maxDaysToFix':carType['maxDaysToFix']}

def assignRandomCars(carsOwned, carTypes, carList):
    for x in range(carsOwned):
        #Get a random car
        carType = random.choice(carTypes)
        carList.append(newVehicle(x+1, 'Active', 0, carType))

def addAdditionalVehicle(carTypes,carList):
    carType = random.choice(carTypes)
    newCarId = len(carList) + 1
    carList.append(newVehicle(newCarId, 'Damaged', 3, carType))


# Generate a list of our cars
assignRandomCars(carsOwned, carTypes, carList)

# Start our Simulation
for x in range(daysToSimulate):
    # Find out which cars are going on a mission today
    activeCars = getCarsOnMissionToday(carList, minCarsToSendOnHunt, maxCarsToSendOnHunt)

    # If you run out of gas you effectively lose the game
    if(gasOwned > 0):
        gasUsedToday = gasUsed(activeCars, minMilesDrivePerDay, maxMilesDrivePerDay)
        gasOwned -= gasUsedToday
        gasUsedInGame += gasUsedToday

        didWeFindATankerToday = percentDieRoll(chanceToGetTanker)
        didWeFindANewVehicleToday = percentDieRoll(chanceOfFindingVehicleOnScout)

        # We found a tanker, kick off winning a tanker.
        if(didWeFindATankerToday and len(activeCars) > 0):
            gasWon = tankerResult(gasPerTanker)
            gasOwned += gasWon
            tankersCaptured += 1
            gasEarnedInGame += gasWon
            print("Master Blaster!  Tanker Captured! {Amount}".format(Amount=gasWon))

        # Add a random car to our "Inventory"
        if(didWeFindANewVehicleToday and len(activeCars) > 0):
            addAdditionalVehicle(carTypes,carList)

        #Update our Cars based on todays events
        totalBreakdowns = dailyCarResults(carList, didWeFindATankerToday, activeCars, totalBreakdowns)

    print("Day {day}".format(day=x))
    printCarStatus(carInventoryStatus(carList))
    print("Current Gas : {gasOwned} (Gas Used:{gasUsedToday} Cars On Mission:{activeCars})".format(gasOwned=round(gasOwned,2), gasUsedToday= gasUsedToday, activeCars=len(activeCars)))
    print("")

## Return out the result of our simulation
print("")
print("Game Results")
print("--------------------------")
print("Tankers Captured: {captured} \t\t Ending Gas: {endGame} \t\t Gas Earned: {gasEarned} \t\t Gas Used {gasUsed} \t\t Total Breakdowns {totalBreakdowns}".format(captured=tankersCaptured, endGame=round(gasOwned,2), gasEarned=round(gasEarnedInGame,2), gasUsed=round(gasUsedInGame,2), totalBreakdowns=round(totalBreakdowns,2)))
printCarStatus(carInventoryStatus(carList))
printCarDisplay(carList)