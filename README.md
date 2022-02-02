# unipark
Unipark Evaluation Tools

## Usage with Docker

### Build the image
Run `docker build -t unipark-notebook .`

### Run the image
Basically you can run this container with 
```sh
docker run --rm -it -p 8888:8888 -v work:/home/jovyan/work unipark-notebook 
```
where 8888 is the port you can access the jupyter notebook server and work is your working directory.
However, using this setup any changes to the notebooks in the `notebook` directory will not be persisted. Also your work
and data directory are likely to get mixed. Therefore, see the recommended mounting options below!

#### Recommended mounting options
Finally, we will come up with a `docker run` command similar to this one:
```sh
docker run --rm -it \
    -p 8888:8888 \
    -v data:/home/$(id -un)/data \
    -v work:/home/$(id -un)/work \
    -v notebooks:/home/$(id -un)/notebooks \
    -u 0 \
    -e NB_UID=$(id -u) -e NB_USER=$(id -un) \
    -e NB_GID=$(id -g) -e NB_GROUP=$(id -gn) \
    -e CHOWN_HOME=1 -e CHOWN_HOME_OPTS='-R'\
    unipark-notebook
```

docker run --rm -it \
    -p 8888:8888 \
    -v data:/home/jovyan/work/data \
    -v work:/home/jovyan/work/work \
    -v notebooks:/home/jovyan/work/notebooks \
    --user $(id -u) --group-add users\
    unipark-notebook
```
where
- `data` is a folder, in which your downloaded unipark-csvs are stored
- `work` is a folder, in which you want to store your results and
- `notebooks` is a folder, in which you store your notebooks. Keep in mind: you mount over the existing notebooks 
folder! Thus, it will contain only the notebooks from the local folder that is mounted. Make sure to copy the notebooks 
you would like to use into that folder. E.g. all [our default notebooks](notebooks).

The command above also make use of the `-u` flag (also known as `--user`). This allows the notebooks user use the same 
uid as your local user (and therefore has write permissions to mounted folders).
