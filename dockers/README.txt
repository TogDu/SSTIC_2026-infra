#configure diode_dest and diode src as needed
# data folder contains:
#   - data/prod: dockers data as present on challenge production server (real flags, crypto key & config)
#   - data/challengers: dockers data as supplied to participant after step3 (flag placeholders, test config, no ignition for step3)
# switching from one version to the other is done by modifying dockerfiles 

docker build -t diode_dst diode_dest
docker build -t diode_src diode_dest

# for step2:

cd step2
docker-compose up

# for step3
cd step3
# for challengers version: 
# add your own lobster_ignition.bin file in step3/inputs folder, uncomment volume block in step3/compose.yaml
docker-compose up
