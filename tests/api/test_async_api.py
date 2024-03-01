import asyncio
import pytest

from pyDataverse.api import NativeApi


class TestAsyncAPI:

    @pytest.mark.asyncio
    async def test_async_api(self, native_api):

        async with native_api:
            tasks = [native_api.get_info_version() for _ in range(10)]
            responses = await asyncio.gather(*tasks)

        assert len(responses) == 10
        for response in responses:
            assert response.status_code == 200, "Request failed."
