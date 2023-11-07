const { RekognitionClient, DetectFacesCommand } = require("@aws-sdk/client-rekognition");
const rekoClient = new RekognitionClient();
const AWS = require('@aws-sdk/client-s3');
const s3 = new AWS.S3();

exports.handler = async (event, callback) => {
    console.log("Event: ",JSON.stringify(event));

    const bucketName = event.Records[0].s3.bucket.name;
    const objectName = event.Records[0].s3.object.key;
    const fileName = event.Records[0].s3.object.key.split(/[\/.]+/)[1]
    const s3Bucket = 's3-data-tcc-processed-rekognition';

    console.log("Bucket: ",bucketName)
    console.log("Object: ", objectName)

    const detectFacesCommand = new DetectFacesCommand({
        Image: {
            S3Object: {
                Bucket: bucketName,
                Name: objectName
            }
        },
        Attributes: ['ALL']
    });

    try {
        const response = await rekoClient.send(detectFacesCommand);

        const extractedInfo = response.FaceDetails.map(face => ({
            AgeRange: face.AgeRange,
            Confidence: face.Confidence,
            Emotions: face.Emotions.map(emotion => ({
                Type: emotion.Type,
                Confidence: emotion.Confidence
            })),
            Gender: face.Gender,
            Quality: face.Quality,
            Sunglasses: face.Sunglasses
        }));

        console.log("Extracted Face Information:", JSON.stringify(extractedInfo));
        const jsonBody = JSON.stringify(extractedInfo, null, 2);
        
        const params = {
            Bucket: s3Bucket,
            Key: `${fileName}.json`,
            Body: jsonBody,
            ContentType: 'application/json',
        };
        
        const s3Response = await s3.putObject(params).promise();
        callback(null, s3Response);
        console.log(`File uploaded to S3: s3://${s3Bucket}/${fileName}.json`);
        
    } catch (e) {
        console.log(e);
        throw new Error(e.message);
    }
};
