node {
    CONTAINER_REGISTRY = 'sivarp'
    COMPONENT = "gists-api"

    def now = new Date()
    String timestamp = now.format("yyMMddHHmm", TimeZone.getTimeZone('UTC'))
    stage("Checkout") {
        // git checkout
        git branch: 'main', url: 'https://github.com/sivarp/code-2-prod.git'
    }
    stage("Build and Test") {
        // compile, build and package
        // multi stage build (test)
        // versionise the tags appropriate
        
        // if it's dev , add version timestamp
        // if it's prod, use semver as such
        String version = readFile("VERSION").trim()
        int buildRetCode = sh (script: "docker build -t ${CONTAINER_REGISTRY}/${COMPONENT}:${version}-${timestamp} .", returnStatus: true)
        if (buildRetCode != 0 ) { error "failed on docker build step" }

    }
    stage("Security test") {
        // trivvy vulnerability
    }
    stage("Publish to Docker") {
        // anonymous publish or use withcreds
        String version = readFile("VERSION").trim()
        sh "docker push ${CONTAINER_REGISTRY}/${COMPONENT}:${version}-${timestamp}"
    }
}