FROM jupyter/minimal-notebook

COPY requirements.txt .
RUN mamba install --quiet --yes --file=requirements.txt && \
    rm requirements.txt && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

COPY README.md .
COPY notebooks notebooks

COPY unipark /opt/PyModules/unipark
COPY LICENSE /opt/PyModules/unipark
ENV PYTHONPATH=/opt/PyModules
