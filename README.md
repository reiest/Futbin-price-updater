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
### 1. Do this only when you need a **new list** of players you want to find
Go to [futbin](https://www.futbin.com/22/players)'s player page and choose your own filters based on which players you want. I have selected all icons between 200 and 450'000 coins. My URL will look like this:

![Players page](fig/Futbinlink.png)

Copy your URL and open [findID.py](findID.py). Change your URL on page 18
```python
URL = 'https://www.futbin.com/22/players?page=1&xbox_price=200-450000&version=icons'
```

## How it works

## Notes