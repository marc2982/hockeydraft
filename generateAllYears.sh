for i in {1996..2024}; do
    if [ -d $i ]; then
        ./run_locally.py $i;
    else
        echo "skipping $i";
    fi
done

