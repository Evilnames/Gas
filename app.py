import random, datetime, math

gasOwned = 1000
gasEarnedInGame = 0
gasUsedInGame   = 0
gasPerTanker = [1000, 2500, 3500, 5500, 6500, 9000, 11500]
carsOwned = 10
carsToSendOnHunt = 3
#https://madmax.fandom.com/wiki/Category:Vehicles
carTypes = [
                {'type':'Pickup Truck', 'mpg':15, 'maxCrew': 4, 'chanceOfDestroy':5, 'breakDownRisk':10, 'breakDownRiskCombat':20, 'maxDaysToFix':7},
                {'type':'Buggy', 'mpg':25, 'maxCrew':4, 'chanceOfDestroy':3, 'breakDownRisk':5, 'breakDownRiskCombat':4, 'maxDaysToFix':4},
                # War Rig
                {'type':'War Rig', 'mpg':15, 'maxCrew':25, 'chanceOfDestroy':2, 'breakDownRisk':35, 'breakDownRiskCombat':10, 'maxDaysToFix':35},
                {'type':'Bus', 'mpg':10, 'maxCrew':15, 'chanceOfDestroy':1, 'breakDownRisk':20, 'breakDownRiskCombat':10, 'maxDaysToFix':20},
                # Based on the Ford Inceterceptor from Original Mad Max
                {'type':'Interceptor', 'mpg':30, 'maxCrew':2, 'chanceOfDestroy':2, 'breakDownRisk':9, 'breakDownRiskCombat':12, 'maxDaysToFix':3},
                # Gyrocopter mostly a scout thing, getting into combat isn't useful
                {'type':'Gyrocopter', 'mpg':5, 'maxCrew':1, 'chanceOfDestroy':10, 'breakDownRisk':40, 'breakDownRiskCombat':25, 'maxDaysToFix':45},
            ]
milesDrivenPerDay = 30
chanceToGetTanker = 3
daysToSimulate = 365

carList = []

# Used for most things in this simulation, testing against a 100% chance
def percentDieRoll(chance):
    roll = random.randrange(1,100)
    return chance > roll

# How much gas is used when we go on a mission
def gasUsed(activeCars, milesDriven):
    totalGasUsed = 0
    for car in activeCars:
        totalGasUsed += milesDrivenPerDay / car['mpg']

    return totalGasUsed

# Which type of tanker did we bag today?
def tankerResult(gasInATanker):
    capturedTanker = random.randrange(1, len(gasInATanker))
    return gasInATanker[capturedTanker]


# Get a list of cars going out on missions today
def getCarsOnMissionToday(cars, carsToSendOnHunt):
    activeCars = list(filter(lambda car: car['status'] == 'Active', cars))
    if(carsToSendOnHunt > len(activeCars)):
        carsToSendOnHunt = len(activeCars)

    if(carsToSendOnHunt == 0):
        return []
    else:
        return random.sample(activeCars, k=carsToSendOnHunt)

# Process results for the day for each car
def dailyCarResults(cars, tankerResult, activeCars):
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
                    car['status'] = 'Damaged'
                    car['repairDays'] = random.randrange(1,car['maxDaysToFix'])
                    amIDead = percentDieRoll(car['chanceOfDestroy'])
                    if(amIDead):
                        car['status'] = 'Destroyed'
                
                car['missions'] = car['missions'] + 1

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

def assignRandomCars(carsOwned, carTypes, carList):
    for x in range(carsOwned):
        #Get a random car
        carType = random.choice(carTypes)

        carList.append({'carId':x + 1, 'status':'Active', 'missions':0, 'repairDays' : 0, 'type':carType['type'], 'mpg':carType['mpg'], 'maxCrew':carType['maxCrew'], 'chanceOfDestroy':carType['chanceOfDestroy'], 'breakDownRisk':carType['breakDownRisk'], 'breakDownRiskCombat':carType['breakDownRiskCombat'], 'maxDaysToFix':carType['maxDaysToFix']})

# Generate a list of our cars
assignRandomCars(carsOwned, carTypes, carList)

# Start our Simulation
for x in range(daysToSimulate):
    # Find out which cars are going on a mission today
    activeCars = getCarsOnMissionToday(carList, carsToSendOnHunt)

    gasUsedToday = gasUsed(activeCars, milesDrivenPerDay)
    gasOwned -= gasUsedToday
    gasUsedInGame += gasUsedToday

    didWeFindATankerToday = percentDieRoll(chanceToGetTanker)
    if(didWeFindATankerToday and len(activeCars) > 0):
        gasWon = tankerResult(gasPerTanker)
        gasOwned += gasWon
        gasEarnedInGame += gasWon
        print("Master Blaster!  Tanker Captured! {Amount}".format(Amount=gasWon))

    #Update our Cars based on todays events
    dailyCarResults(carList, didWeFindATankerToday, activeCars)

    print("Day {day}".format(day=x))
    printCarStatus(carInventoryStatus(carList))
    print("Current Gas : {gasOwned} (Gas Used:{gasUsedToday} Cars On Mission:{activeCars})".format(gasOwned=round(gasOwned,2), gasUsedToday= gasUsedToday, activeCars=len(activeCars)))
    print("")

print("")
print("Game Results")
print("--------------------------")
print("Ending Gas: {endGame} \t\t Gas Earned: {gasEarned} \t\t Gas Used {gasUsed}".format(endGame=round(gasOwned,2), gasEarned=round(gasEarnedInGame,2), gasUsed=round(gasUsedInGame,2)))
printCarStatus(carInventoryStatus(carList))
printCarDisplay(carList)