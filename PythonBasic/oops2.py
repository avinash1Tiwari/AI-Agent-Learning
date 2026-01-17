class Man:
    color = "black"

    # def __init__(self):
    #     print("passing no any parameters in constructor")

    def __init__(self,age=None,name=None):
        if(name == None):
             print("passing no any parameters in constructor")
        else:
            self.name = name
            self.age = age

    @staticmethod
    def solve():
        print("my name is avinash tiwari")

m1 = Man()
m2 = Man("avinash",22)
Man.solve()
m1.solve()


# print("m1-details : ",m1.name)
print("m2-details : ", "m2-name : " , m2.name , ", " , m2.age)