import pandas as pd, requests

mps = pd.read_csv("mps.csv")

for i in range(0, len(mps)):
    FirstName = mps.loc[i, "First name"]
    Lastname = mps.loc[i, "Last name"]
    Constituency = mps.loc[i, "Constituency"]
    URI = mps.loc[i, "Uri"]
    Name = f"{FirstName} {Lastname}"
    url = f"http://lda.data.parliament.uk/members.json?fullName={Name}"
    res = requests.get(url)
    results = res.json()
    Namelist = results["result"]["items"]
    prefixes = ["Mr", "Sir", "Ms", "Dr"]
    if URI != "":
        if len(Namelist) == 1:
            for name in Namelist:
                if name["constituency"]["label"]["_value"] == Constituency:
                    uri = name["_about"]
                    mps.loc[i, "Uri"] = uri
                else:
                    print(f"Name Matches but Constituency doesnt for {Name}")
        else:
            if len(Namelist) == 0:
                found = False
                for prefix in prefixes:
                    NewName = f"{prefix} {Name}"
                    url = f"http://lda.data.parliament.uk/members.json?fullName={NewName}"
                    res = requests.get(url)
                    results = res.json()
                    Namelist = results["result"]["items"]
                    if len(Namelist) > 0:
                        for name in Namelist:
                            if name["constituency"]["label"]["_value"] == Constituency:
                                uri = name["_about"]
                                mps.loc[i, "Uri"] = uri
                                found = True
                            else:
                                print(f"Name Matches but Constituency doesnt for {Name}")
                if not found:
                    print(f"No Listing for {Name}")
            if len(Namelist) > 1:
                print(f"More than one Listing for {Name}")

mps.to_csv("mps.csv")