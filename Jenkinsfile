// Semana 11: Jenkins usa exactamente el mismo ejecutor Docker que GitHub Actions.
// Configurar como "Pipeline script from SCM"; rama */main; Script Path: Jenkinsfile.
pipeline {
    agent any
    options { timestamps(); disableConcurrentBuilds(); timeout(time: 180, unit: 'MINUTES') }
    triggers { pollSCM('H/5 * * * *') } // PC con Jenkins en localhost; webhook opcional si está accesible
    parameters {
        booleanParam(name: 'REQUIRE_TESTLINK', defaultValue: false, description: 'Exigir sincronización real con TestLink (credencial testlink-devkey)')
        booleanParam(name: 'SMOKE_ONLY', defaultValue: false, description: 'Solo diagnóstico de k6; NO sustituye entrega completa')
    }
    environment { CI_PIPELINE='jenkins'; PYTHONIOENCODING='utf-8' }
    stages {
        stage('01 Checkout') { steps { checkout scm } }
        stage('02 Build Docker') { steps { bat 'python ci\\execute.py build' } }
        stage('03 Environment') { steps { bat 'python ci\\execute.py environment' } }
        stage('04 Unit tests') { steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') { bat 'python ci\\execute.py unit' } } }
        stage('05 Selenium TC01-TC41') { steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') { bat 'python ci\\execute.py selenium' } } }
        stage('06 Playwright TC01-TC41') { steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') { bat 'python ci\\execute.py playwright' } } }
        stage('07 Functional Semana 9') { steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') { bat 'python ci\\execute.py functional' } } }
        stage('08 UAT Behave y regresión') { steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') { bat 'python ci\\execute.py uat' } } }
        stage('09 k6 Performance (dos apps) R01-R10') {
            steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') {
                script { bat "python ci\\execute.py performance${params.SMOKE_ONLY ? ' --smoke' : ''}" }
            } }
        }
        stage('10 k6 Stress (dos apps) E01-E10') {
            steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') {
                script { bat "python ci\\execute.py stress${params.SMOKE_ONLY ? ' --smoke' : ''}" }
            } }
        }
        stage('11 Security (dos apps) k6 S01-S10 y DOM') { steps { catchError(buildResult:'FAILURE',stageResult:'FAILURE') { bat 'python ci\\execute.py security' } } }
        stage('12 TestLink XML-RPC') {
            when { expression { return params.REQUIRE_TESTLINK } }
            steps {
                withCredentials([string(credentialsId:'testlink-devkey',variable:'TESTLINK_DEVKEY')]) {
                    withEnv(['REQUIRE_TESTLINK=1']) {
                        catchError(buildResult:'FAILURE',stageResult:'FAILURE') { bat 'python ci\\execute.py testlink' }
                    }
                }
            }
        }
        stage('13 Reports') { steps { bat 'python ci\\execute.py reports' } }
        stage('14 Quality Gates') {
            steps {
                script {
                    withEnv(["REQUIRE_TESTLINK=${params.REQUIRE_TESTLINK ? '1' : '0'}"]) {
                        bat 'python ci\\execute.py quality'
                    }
                }
            }
        }
    }
    post {
        always {
            junit testResults:'reports/**/*.xml', allowEmptyResults:true
            archiveArtifacts artifacts:'reports/**', allowEmptyArchive:true
            bat 'python ci\\execute.py cleanup'
        }
    }
}
