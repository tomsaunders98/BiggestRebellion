import requests, pandas as pd
from datetime import date
from git import Repo

def getDivisioins(date):
    url = f"http://lda.data.parliament.uk/commonsdivisions/date/{date}.json"
    res = requests.get(url)
    divisions = res.json()
    divlist = divisions["result"]["items"]
    uins =[]
    if len(divlist) > 0:
        print("New Divisions:")
        for div in divlist:
            divtitle = div["title"]
            uin = div["uin"]
            print(f"{divtitle} ({uin})")
            uins.append(uin)
        return uins
    else:
        return uins

def ProcessVotes(uin):
    leaders = pd.read_csv("Leader.csv")
    MPS = pd.read_csv("mps.csv")
    leaderUri = leaders["Uri"].tolist()
    url = f'http://lda.data.parliament.uk/commonsdivisions.json?uin={uin}'
    res = requests.get(url)
    result = res.json()
    votes = result["result"]["items"][0]["vote"]
    # Get Leaders Votes:
    for vote in votes:
        member = vote["member"][0]["_about"]
        votetype = vote["type"]
        if member in leaderUri:
            #Increase Leader Vote type
            leaders.loc[leaders["Uri"] == member, "Vote"] = votetype
            Total = leaders.loc[leaders["Uri"] == member, "Total"]
            Total = Total + 1
            leaders.loc[leaders["Uri"] == member, "Total"] = Total
            # Increase overall Total
            Total = leaders.loc[leaders["Party"] == "Total", "Total"]
            Total = Total + 1
            leaders.loc[leaders["Party"] == "Total", "Total"] = Total
            leaders.to_csv("Leader.csv", index=False)
    # Assign Rebel
    for vote in votes:
        member = vote["member"][0]["_about"]
        votetype = vote["type"]
        Name = vote["memberPrinted"]["_value"]
        if len(MPS.loc[MPS["Uri"] == member, "Party"]) == 0:
            print(f"No entry for {Name}, with URI {member}")
            continue
        else:
            Party = MPS.loc[MPS["Uri"] == member, "Party"].values[0]
        if len(leaders.loc[leaders["Party"] == Party, "Vote"]) == 0:
            #Smaller Party
            print(f"Not Tracking for {Name} of {Party}")
            continue
        notvoted = leaders.loc[leaders["Party"] == Party, "Vote"].isna().values
        if not notvoted[0]:
            CorrectVote = leaders.loc[leaders["Party"] == Party, "Vote"].values[0]
            if votetype != CorrectVote:
                print(f"{Name} rebelled, {Party} voted {CorrectVote} and {Name} voted {votetype}.")
                Rebel = MPS.loc[MPS["Uri"] == member, "Rebel"].values[0]
                Rebel = Rebel + 1
                MPS.loc[MPS["Uri"] == member, "Rebel"] = Rebel
                MPS.to_csv("mps.csv", index=False)

def HighlightParty(s):
    if s.Party == "Labour":
        return ['background-color: #CC433F']*3
    if s.Party == "Conservative":
        return ['background-color: #585FD6']*3
    if s.Party == "Scottish National Party":
        return ['background-color: #D6C552']*3
    if s.Party == "Liberal Democrat":
        return ['background-color: #E08E55']*3
    if s.Party == "Plaid Cymru":
        return ['background-color: #40612C']*3
    if s.Party == "Green":
        return ['background-color: #65B352']*3
    if s.Party == "DUP":
        return ['background-color: #CC6B63']*3
    else:
        return ['background-color: White']*3

def CreateFile(filename,df, styles: bool = False):
    df = df.rename(columns={"Rebel": "Rebellions"}, errors="raise")
    df = df.head(10)
    df["Rebellions"] = df["Rebellions"].apply(lambda x: str(int(x)) + " %")
    if styles:
        html = df.style.apply(HighlightParty, axis=1)
        html = html.hide_index()
        html = html.render()
    else:
        html = df.to_html(index=False)
    result = '''
    <html>
        <head>
            <style type="text/css">
                body {
                    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";
                    font-size: 1rem;
                    font-weight: 400;
                    line-height: 1.5;
                    color: #212529;
                    text-align: left;
                }
                table {
                    border-collapse: collapse;
                    border: 0;
                }
                table td, table th {
                    padding: .75rem;
                    vertical-align: top;
                    border-bottom: 0;
                    border-left: 0;
                    border-right: 0;
                    text-align: center;
                }
                *, ::after, ::before {
                    box-sizing: border-box;
                }
            </style>
        </head>
    <body>
'''
    result = result + html

    with open(filename, 'w') as f:
        f.write(result)

def gentables():
    leaders = pd.read_csv("Leader.csv", index_col=False)
    MPS = pd.read_csv("mps.csv", index_col=False)
    ## Formatting CSV for Production
    MPS["Name"] = MPS["First name"] + " " + MPS["Last name"]
    MPS = MPS.drop(columns=['RT', 'First name', 'Last name', 'Constituency', 'Uri'])
    cols = ['Name', 'Party', 'Rebel']
    MPS = MPS[cols]
    ## All Rebels
    for i in range(0, len(leaders) - 1):
        LeaderValue = leaders.loc[i, "Total"]
        LeaderParty = leaders.loc[i, "Party"]
        MPS["Rebel"] = MPS["Rebel"].apply(lambda x: (x / LeaderValue) * 100 if MPS["Party"].values[0] == LeaderParty else x)
    MPS = MPS.sort_values(by=['Rebel'], ascending=False)
    CreateFile('allRebel.html', MPS, styles=True)
    ## Conservative Rebels
    CONS = MPS[MPS["Party"] == "Conservative"]
    CreateFile('ConsRebel.html', CONS)
    ## Labour Rebels
    LAB = MPS[MPS["Party"] == "Labour"]
    CreateFile('LabRebel.html', LAB)
    ## SNP Rebels
    SNP = MPS[MPS["Party"] == "Scottish National Party"]
    CreateFile('SNPRebel.html', SNP)

def upload(fielist):
    







def main():
    today = date.today()
    gentables()
    # uins = getDivisioins(today)
    # if len(uins) == 0:
    #     print("No Divisions today")
    # else:
    #     for uin in uins:
    #         print(f"Proccsing Division {uin}:")
    #         ProcessVotes(uin)
if __name__ == "__main__":
    main()
