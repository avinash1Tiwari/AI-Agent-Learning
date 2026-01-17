def findMax(arr,index):
    if index == len(arr)-1:
        return arr[index]

    return max(arr[index],findMax(arr,index+1))
    


arr = [45,2,3,1,6,56,78,34,10]
print(findMax(arr,0))
print(max(arr))