FROM jupyter/minimal-notebook

COPY requirements.txt .
RUN mamba install --quiet --yes --file=requirements.txt && \
    rm requirements.txt && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

ENV JUPYTER_ENABLE_LAB=yes

#RUN mkdir notebooks data
#RUN chmod -R 777 .

COPY --chown=jovyan --chmod=777 README.md .
COPY --chown=jovyan --chmod=777 notebooks default_notebooks

COPY unipark /opt/PyModules/unipark
COPY LICENSE /opt/PyModules/unipark
ENV PYTHONPATH=/opt/PyModules
