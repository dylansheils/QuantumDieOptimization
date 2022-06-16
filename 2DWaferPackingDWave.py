import math
import dimod

# Define the chips:
chips = ["chipA", "chipB"]
chipHeights = [0, 1, 2, 100]
chipWidths = [0, 4, 3, 100]
chipProfits = [0, 5, 10, 2]

# Consider chip rotations:
chipsToAdd = []
for entry in range(1, len(chips)):
    newEntry = chips[entry] + "Rotated"
    chipsToAdd.append(newEntry)
    chipHeights.append(chipWidths[entry])
    chipWidths.append(chipHeights[entry])
    chipProfits.append(chipProfits[entry])
# Just to not influence the iteration
for newEntry in chipsToAdd:
    chips.append(newEntry)

# segements horizontal
horizontalDieSegments = [4, 3]
# segments verticle
verticleDieSegments = [1, 2]

if(len(horizontalDieSegments) != len(verticleDieSegments)):
    print("ERROR: Dimensional Mismatch of Horizontal and Verticle Die Segments!")

# Code to print the die shape
def printDie(horizontalDieSegments, verticleDieSegments):
    print("Die Shape:")
    print("-" * 50)
    for index in range(len(verticleDieSegments)):
        for _ in range(verticleDieSegments[index]):
            print(("-" * horizontalDieSegments[index]).center(50," "))
    print("-" * 50)

# Print out the specified die
printDie(horizontalDieSegments, verticleDieSegments)

# Generate an overlay on die of sufficient mesh size
minChipHeight = min(chipHeights[1:])
minChipWidth = min(chipWidths[1:])
numBinsVerticleSegment = [math.floor(((horizontalDieSegments[i] * verticleDieSegments[i]) / (minChipHeight * minChipWidth))) for i in range(len(verticleDieSegments))]

# Define 2D occupancy
occupancy = [[dimod.Binary(str("(" + str(i) + "," + str(j) + ")")) for i in range(numBinsVerticleSegment[j])] for j in range(len(numBinsVerticleSegment))]
# Define integer choice
choiceAtOccupancy = [[[dimod.Binary(str("(" + str(i) + "," + str(j) + "),D:" + str(k) + ")")) for k in range(len(chipProfits))] for i in range(numBinsVerticleSegment[j])] for j in range(len(numBinsVerticleSegment))]
print(choiceAtOccupancy)
# Make model
cqm = dimod.CQM()

# Set the objective function (minimize the negative of total profit throughout each bin):
cqm.set_objective(-sum([sum([sum([choiceAtOccupancy[i][j][k]*chipProfits[k] for k in range(len(chipProfits))]) for j in range(len(occupancy[i]))]) for i in range(len(occupancy))]))

# One must make exactly one binary choice at a point of occupancy
for i in range(len(choiceAtOccupancy)):
    for j in range(len(choiceAtOccupancy[i])):
        cqm.add_constraint(sum([choiceAtOccupancy[i][j][k] for k in range(len(chipProfits))]) <= 1)

# Well...gotta restrict the dimensions
for i in range(len(choiceAtOccupancy)): # For each horizontal
    cqm.add_constraint(sum([sum([choiceAtOccupancy[i][j][k]*chipWidths[k] for k in range(len(chipProfits))]) for j in range(len(choiceAtOccupancy[i]))]) <= horizontalDieSegments[i])

# Area has to be conserved as well as horizontal dimension
cqm.add_constraint(sum([sum([sum([choiceAtOccupancy[i][j][k]*chipWidths[k]*chipHeights[k] for k in range(len(chipProfits))]) for j in range(len(choiceAtOccupancy[i]))]) for i in range(len(choiceAtOccupancy))]) <= sum([horizontalDieSegments[i] * verticleDieSegments[i] for i in range(len(choiceAtOccupancy))]))

from dwave.system import LeapHybridCQMSampler
sampler = LeapHybridCQMSampler()     
sampleset = sampler.sample_cqm(cqm, label='2D Chip Packing with Cost')
sampleset = sampleset.filter(lambda row: row.is_feasible)
print(sampleset.first)