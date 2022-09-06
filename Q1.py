from itertools import starmap
import random 
from multiprocessing.pool import ThreadPool

def simulate(N, samplespace, passes, output):
    result = []
    for i in range(passes):
        total, outcomes = 1, []
        for i in range(N):
            if(total==0):
                pass
            else:
                choice = random.choice(samplespace)
                if(choice=="Heads"):
                    total += 1
                else:
                    total -= 0.5
                outcomes.append(choice)
        result.append(total)
    output.extend(result)
def run(n, N, samplespace, passes):
    output = []
    pool = ThreadPool(processes=n)
    for i in range(n):      
        result = pool.apply_async(simulate, [N, samplespace, int(passes/n), output]) 
    pool.close()
    pool.join()
    return output
def transformToRV(output, sample=True):
    output = {k:v for k,v in [(i, output.count(i)) for i in set(output)]}
    trials = sum([i for i in output.values()])
    for i in output:
        if(sample):
            output[i] = output[i]/(trials-1)
        else:
            output[i] = output[i]/trials
    return output
def analyze(output, resolution=2):
    mean = round(sum([i*output[i] for i in output]), resolution)
    var = round(sum([((i-mean)**2)*output[i] for i in output]), resolution)
    
    return mean, var
if __name__ == "__main__":

    samplespace = ["Heads", "Tails"]
    N = 100000
    passes = 10000
    
    output = analyze(transformToRV(run(100, N, samplespace, passes)))

    print("mean =", output[0], "and", "var =", output[1])