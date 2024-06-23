for i in {1996..2024}; do
    if [ -d $i ]; then
        ./publish.sh $i;
    else
        echo "skipping $i";
    fi
done

