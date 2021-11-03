# Futbin price finder
Python program which goes through the last 500 sales of players and calculate buy prices.

## Installation
Begin by cloning the repository using your **console**:
```console
git clone https://github.com/fskickz/Futbin-price-updater.git
````
Install the required modules:
```console
pip install -r requirements.txt
```

## How to use
### 1. You only have to do this once
Go to [futbin](https://www.futbin.com/22/players)'s player page and choose your own filters based on which players you want. I have selected all icons between 200 and 450'000 coins. My URL will look like this:

![Players page](fig/Futbinlink.png)

Copy your URL and open [findID.py](findID.py). Change your URL on line 16
```python
URL = 'https://www.futbin.com/22/players?page=1&xbox_price=200-450000&version=icons'
```
You are now ready to run [findID.py](findID.py)
When you run [findID.py](findID.py), you will be prompted to type in the name of the directory you want to create. In my instance i call it "icons". This will create a new directory with a text- and excelfile. 

**Checklist:**
* Have a new directory
* Have a txt and excel file
* txt file should look like this:
```txt
'Deco 85': 239027,
'Cole 85': 255354,
'Guardiola 85': 243782,
'Inzaghi 85': 239072,
'Koeman 85': 247303,
```

### 2. Find buy prices based on sales history
Open [salehistory.py](salehistory.py) and change line 11 and 12.
```python
platform = "xone"  # Xbox = xone,    Playstation = ps,   PC = pc
directory = "icons"  # Change to directory you want to use (category)
```
The directory should be set to the directory you want to use. I want to find the price of icons. You can set this to the directory you just created if you want. The idea is that you can create multiple groups of players. **Ex:** Icons under 450k, all hero cards, silvers etc... If you want to make a new group, follow step 1. You only have to follow step 1 if you want a new group/filter.

**Checklist:**
* You have a directory with a excel and txt file
* Changed line 11 and 12 to your needs
* Followed the installation

Now you are ready to run [salehistory.py](salehistory.py)

## Result and examples

## Notes