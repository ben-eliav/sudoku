# Creating the Puzzles
The puzzles were generated using code from [QQWing](https://qqwing.com/download.html). Specifically, I used the C++ downloadable version and ran the following code:

```
./configure
make
./qqwing --generate 200 --difficulty easy --csv > easy.csv
./qqwing --generate 200 --difficulty intermediate --csv > medium.csv
./qqwing --generate 200 --difficulty expert --csv > expert.csv
```

I did not use this code for anything besides creating the puzzles.