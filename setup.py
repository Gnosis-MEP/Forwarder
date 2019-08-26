from setuptools import setup

setup(
    name='forwarder',
    version='0.1',
    description='Service responsible for sending the notification of matched events to the subscribers in the correct output format, as detailed by the inputs from the Query Register.',
    author='Felipe Arruda Pontes',
    author_email='felipe.arruda.pontes@insight-centre.org',
    packages=['forwarder'],
    zip_safe=False
)
