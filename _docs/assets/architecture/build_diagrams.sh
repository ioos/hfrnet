
# D2
# d2 fmt file.d2
# d2 --theme 300 file.d2
# d2 --theme 300 file.d2 file.png

for FILE in *.d2; do d2 fmt $FILE; d2 --theme 300 $FILE; d2 --theme 300 $FILE $FILE:r.png; done


# Structurizr CLI to d2
structurizr-cli export -f d2 -w workspace.dsl -o ./c4
cd ./c4
for FILE in *.d2; do d2 $FILE; d2 $FILE:r.png; done
