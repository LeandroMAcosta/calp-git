rm -rf 1.txt 2.txt 3.txt 4.txt 5.txt 6.txt 7.txt .calp .git

calp init

echo 'hello world' > README.md
calp add README.md
calp commit -m 'first commit from master (A)'

echo 'def main(): ...' > main.py 
calp add main.py
calp commit -m 'second commit from master (B)'

calp checkout -b feature
# Me muevo a master    ===========================
calp checkout master

echo '# my algorithm' > algorithms.py
calp add algorithms.py
calp commit -m 'third commit from master (C)'

echo '# my other algorithm' > algorithms.py
calp add algorithms.py
calp commit -m 'fourth commit from master (D)'

# Me muevo a feature ========================
calp checkout feature

# echo '5' > 5.txt
rm main.py
calp add main.py
calp commit -m 'fifth commit from feature (E)'


echo '# my utils' > utils.py
calp add utils.py
calp commit -m 'sixth commit from feature (F)'


# Me muevo a master
calp checkout master

calp rebase feature
