result = {}
for i in range(3, 1005):
    total = 0
    for j in range(3, 1005):
        if(j>i):
            total += 2*(j-i)
        else:
            total += (j-i)**2
    result[i] = total/1002
print({k:result[k] for k in sorted(result, key=result.get)})