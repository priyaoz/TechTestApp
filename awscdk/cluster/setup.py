import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="techtestapp-cluster",
    version="0.0.1",

    description="Create a basic pipeline that deploys the Servian TestTechApp to AWS Cloudformation",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Michael Hoffmann",

    package_dir={"": "techtestapp_cluster"},
    packages=setuptools.find_packages(where="techtestapp_cluster"),

    install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-ecs",
        "aws-cdk.aws-ecs-patterns",
        "aws-cdk.aws-rds",
        "PyYAML",
        "setuptools",
        "jsii~=1.6.0",
        "boto3",
        "toml"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
