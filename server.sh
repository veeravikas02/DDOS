CONNECTION_LIMIT=20
WINDOW_SIZE_SECONDS=10
CONNECTIONS=()

function detect_ddos() {
    while true; do
        sleep $WINDOW_SIZE_SECONDS
        current_time=$(date +%s)
        active_connections=($(printf "%s\n" "${CONNECTIONS[@]}" | awk -v current_time="$current_time" '$1 >= current_time - '"$WINDOW_SIZE_SECONDS"))

        if [ "${#active_connections[@]}" -gt "$CONNECTION_LIMIT" ]; then
            echo "Possible DDoS attack detected: ${#active_connections[@]} connections within $WINDOW_SIZE_SECONDS seconds"
        fi
    done
}

function predict_ddos() {
    python3 predict_ddos.py "$1"
}

function start_server() {
    detect_ddos &

    exec 3<>/dev/tcp/localhost/$1
    echo "Server listening on port $1"

    while true; do
        read -u 3 client_input
        addr="${BASH_REMATCH[1]}"
        echo "Accepted connection from $addr"

        CONNECTIONS+=($(date +%s))

        ddos_probability=$(predict_ddos "$(date +%s)")

        if (( $(echo "$ddos_probability > 0.5" | bc -l) )); then
            echo "Possible DDoS attack detected: Probability = $ddos_probability"
        fi

        echo "Hello, World!" >&3
    done
}

if [ "$#" -eq 1 ]; then
    start_server $1
else
    echo "Usage: $0 <port_number>"
    exit 1
fi
