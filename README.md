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


Finally we will come up with a `docker run` command similar to this one:
```sh
docker run --rm -it \
    -p 8888:8888 \
    -v data:/home/jovyan/data \
    -v work:/home/jovyan/work \
    -v notebooks:/home/jovyan/notebooks \
    unipark-notebook
```
# mount your data to the container!
# by default generated artifacts will be persisted here
# if you want to persist your changes in your notebook 