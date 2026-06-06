def machine_gen():
    machines = [f'dl9hstap{i+1}' for i in range(3)]
    i = 0
    while i < len(machines):
        yield machines[i]
        i = (i + 1) % len(machines)
