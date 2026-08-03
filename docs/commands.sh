sphinx-apidoc -fe -o source/nexoclom2/ ../nexoclom2/
sphinx-build -b html source build/html
sphinx-build -b latex source build/pdf
make latexpdf
