# BullyAlgorithm
## Docker build <nameImageDocker> .
## Docker run -p portlocal:5000 <nameImageDocker> bash -c "python NodeBully.py MiPort Id PortList  PortLeader"
### Example list null
#### Container with port and  id
#### docker run -p 5002:5000 flask bash -c "python NodeBully.py 5002 10" 
#### Container with list and leader 
#### docker run -p 5002:5000 flask bash -c "python NodeBully.py 5002 10 5000 5001 5002  5001 "
