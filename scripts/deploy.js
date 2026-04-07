async function main() {
    const PQRegistry = await ethers.getContractFactory("PQRegistry");

    const registry = await PQRegistry.deploy();

    await registry.waitForDeployment();

    console.log(
        "Contract deployed to:",
        await registry.getAddress()
    );
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});