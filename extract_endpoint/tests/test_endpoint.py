import io
import base64
from http import HTTPStatus
import typing
import pytest
from flask import testing
from azure.storage import blob
from extract_endpoint import azure_utils
from extract_endpoint import crypt_utils
from extract_endpoint import endpoint


endpoint.App.testing = True


@pytest.fixture
def test_client(azure_emulator_coords: azure_utils.StorageCoordinates) -> testing.FlaskClient:
    original_coordinates = endpoint.App.config['AZURE_COORDINATES']
    endpoint.App.config['AZURE_COORDINATES'] = azure_emulator_coords
    yield endpoint.App.test_client()
    endpoint.App.config['AZURE_COORDINATES'] = original_coordinates


@pytest.fixture
def sample_salt() -> str:
    return 'sample salt'


@pytest.fixture
def sample_secret_key() -> typing.Generator:
    original_secret_key = endpoint.App.config['SECRET_KEY']
    endpoint.App.config['SECRET_KEY'] = 'sample secret key'
    yield endpoint.App.config['SECRET_KEY']
    endpoint.App.config['SECRET_KEY'] = original_secret_key


@pytest.fixture
def sample_stream_content() -> str:
    return "Sample stream content"


@pytest.fixture
def sample_stream(sample_stream_content: str) -> io.BytesIO:
    return io.BytesIO(sample_stream_content.encode())


@pytest.fixture
def sample_signature(sample_salt: str, sample_secret_key: str, sample_stream: io.BytesIO) -> str:
    signature = crypt_utils.sign_string(salt=sample_salt, key=sample_secret_key,
                                        data=base64.b64encode(sample_stream.read()).decode('utf-8'))
    sample_stream.seek(0)
    return signature


@pytest.fixture
def sample_filename() -> str:
    return 'test_sample_blob_filename.txt'


def test_frontend(test_client: testing.FlaskClient) -> None:
    assert test_client.get('/').status_code == HTTPStatus.OK


def test_alive(test_client: testing.FlaskClient) -> None:
    get_return = test_client.get('/test_alive')
    assert b'Alive' in get_return.data


def test_robots(test_client: testing.FlaskClient) -> None:
    get_return = test_client.get('/robots933456.txt')
    assert get_return.status_code == HTTPStatus.NOT_FOUND


def test_upload(azure_emulator_coords: azure_utils.StorageCoordinates,
                test_client: testing.FlaskClient,
                azure_service: blob.BlockBlobService,
                sample_salt: str,
                sample_signature: str,
                sample_stream_content: str,
                sample_stream: io.BytesIO,
                sample_filename: str) -> None:

    post_return = test_client.post('/upload_file', data=dict(salt=sample_salt, signature=sample_signature,
                                                             filename=sample_filename,
                                                             file=(sample_stream, sample_filename)))
    assert post_return.status_code == HTTPStatus.CREATED
    assert sample_filename in \
           [blob.name for blob in azure_service.list_blobs(azure_emulator_coords.container)]
    actual_blob = azure_service.get_blob_to_text(azure_emulator_coords.container, sample_filename)
    assert actual_blob.content == sample_stream_content


@pytest.mark.usefixtures('azure_service')
def test_upload_no_key_in_env(test_client: testing.FlaskClient,
                              sample_salt: str,
                              sample_signature: str,
                              sample_stream: io.BytesIO,
                              sample_filename: str) -> None:

    endpoint.App.config['SECRET_KEY'] = endpoint.DEFAULT_ENDPOINT_SECRET_KEY
    with pytest.raises(ValueError):
        test_client.post('/upload_file', data=dict(salt=sample_salt, signature=sample_signature,
                                                   filename=sample_filename, file=(sample_stream, sample_filename)))


@pytest.mark.usefixtures('azure_service')
def test_upload_no_salt(test_client: testing.FlaskClient,
                        sample_signature: str,
                        sample_stream: io.BytesIO,
                        sample_filename: str) -> None:

    post_return = test_client.post('/upload_file', data=dict(signature=sample_signature, filename=sample_filename,
                                                             file=(sample_stream, sample_filename)))
    assert post_return.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures('azure_service')
def test_upload_wrong_salt(test_client: testing.FlaskClient,
                           sample_signature: str,
                           sample_stream: io.BytesIO,
                           sample_filename: str) -> None:

    post_return = test_client.post('/upload_file', data=dict(salt='wrong salt', signature=sample_signature,
                                                             filename=sample_filename,
                                                             file=(sample_stream, sample_filename)))
    assert post_return.status_code == HTTPStatus.BAD_REQUEST

@pytest.mark.usefixtures('sample_signature', 'azure_service')
def test_upload_no_signature(test_client: testing.FlaskClient,
                             sample_salt: str,
                             sample_stream: io.BytesIO,
                             sample_filename: str) -> None:

    post_return = test_client.post('/upload_file', data=dict(salt=sample_salt, filename=sample_filename,
                                                             file=(sample_stream, sample_filename)))
    assert post_return.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures('sample_signature', 'azure_service')
def test_upload_wrong_signature(test_client: testing.FlaskClient,
                                sample_salt: str,
                                sample_stream: io.BytesIO,
                                sample_filename: str) -> None:

    post_return = test_client.post('/upload_file', data=dict(salt=sample_salt, signature='wrong signature',
                                                             filename=sample_filename,
                                                             file=(sample_stream, sample_filename)))
    assert post_return.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures('azure_service')
def test_upload_no_file(test_client: testing.FlaskClient,
                        sample_salt: str,
                        sample_signature: str) -> None:

    post_return = test_client.post('/upload_file', data=dict(salt=sample_salt, signature=sample_signature,
                                                             filename=sample_filename))
    assert post_return.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.usefixtures('azure_service')
def test_upload_no_filename(test_client: testing.FlaskClient,
                            sample_salt: str,
                            sample_signature: str,
                            sample_stream: io.BytesIO) -> None:

    post_return = test_client.post('/upload_file', data=dict(salt=sample_salt, signature=sample_signature,
                                                             filename=sample_filename, file=(sample_stream, '')))
    assert post_return.status_code == HTTPStatus.BAD_REQUEST