"""Test the Transform class."""

from click_extended.utils.casing import Casing


class Case:
    """A case to test for all transform methods."""

    def __init__(
        self,
        value: str,
        upper_case: str,
        lower_case: str,
        meme_case: str,
        snake_case: str,
        screaming_snake_case: str,
        camel_case: str,
        pascal_case: str,
        kebab_case: str,
        train_case: str,
        flat_case: str,
        dot_case: str,
        title_case: str,
        path_case: str,
    ):
        """
        Initialize a new `Case` instance.

        Args:
            value (str):
                The value to test.
            upper_case (str):
                The expected result for the `to_upper_case` method.
            lower_case (str):
                The expected result for the `to_lower_case` method.
            meme_case (str):
                The expected result for the `to_meme_case` method.
            snake_case (str):
                The expected result for the `to_snake_case` method.
            screaming_snake_case (str):
                The expected result for the `to_screaming_snake_case` method.
            camel_case (str):
                The expected result for the `to_camel_case` method.
            pascal_case (str):
                The expected result for the `to_pascal_case` method.
            kebab_case (str):
                The expected result for the `to_kebab_case` method.
            train_case (str):
                The expected result for the `to_train_case` method.
            flat_case (str):
                The expected result for the `to_flat_case` method.
            dot_case (str):
                The expected result for the `to_dot_case` method.
            title_case (str):
                The expected result for the `to_title_case` method.
            path_case (str):
                The expected result for the `to_path_case` method.
        """
        self.value = value
        self.upper_case = upper_case
        self.lower_case = lower_case
        self.meme_case = meme_case
        self.snake_case = snake_case
        self.screaming_snake_case = screaming_snake_case
        self.camel_case = camel_case
        self.pascal_case = pascal_case
        self.kebab_case = kebab_case
        self.train_case = train_case
        self.flat_case = flat_case
        self.dot_case = dot_case
        self.title_case = title_case
        self.path_case = path_case


cases: list[Case] = [
    Case(
        value="",
        upper_case="",
        lower_case="",
        meme_case="",
        snake_case="",
        screaming_snake_case="",
        camel_case="",
        pascal_case="",
        kebab_case="",
        train_case="",
        flat_case="",
        dot_case="",
        title_case="",
        path_case="",
    ),
    Case(
        value="hello world",
        upper_case="HELLO WORLD",
        lower_case="hello world",
        meme_case="hElLo WoRlD",
        snake_case="hello_world",
        screaming_snake_case="HELLO_WORLD",
        camel_case="helloWorld",
        pascal_case="HelloWorld",
        kebab_case="hello-world",
        train_case="Hello-World",
        flat_case="helloworld",
        dot_case="hello.world",
        title_case="Hello World",
        path_case="hello/world",
    ),
    Case(
        value="JSON parser utility",
        upper_case="JSON PARSER UTILITY",
        lower_case="json parser utility",
        meme_case="jSoN pArSeR uTiLiTy",
        snake_case="json_parser_utility",
        screaming_snake_case="JSON_PARSER_UTILITY",
        camel_case="jsonParserUtility",
        pascal_case="JsonParserUtility",
        kebab_case="json-parser-utility",
        train_case="Json-Parser-Utility",
        flat_case="jsonparserutility",
        dot_case="json.parser.utility",
        title_case="Json Parser Utility",
        path_case="json/parser/utility",
    ),
    Case(
        value="make_it WORK",
        upper_case="MAKE_IT WORK",
        lower_case="make_it work",
        meme_case="mAkE_iT wOrK",
        snake_case="make_it_work",
        screaming_snake_case="MAKE_IT_WORK",
        camel_case="makeItWork",
        pascal_case="MakeItWork",
        kebab_case="make-it-work",
        train_case="Make-It-Work",
        flat_case="makeitwork",
        dot_case="make.it.work",
        title_case="Make It Work",
        path_case="make/it/work",
    ),
    Case(
        value="  user-profile ID ",
        upper_case="USER-PROFILE ID",
        lower_case="user-profile id",
        meme_case="uSeR-pRoFiLe Id",
        snake_case="user_profile_id",
        screaming_snake_case="USER_PROFILE_ID",
        camel_case="userProfileId",
        pascal_case="UserProfileId",
        kebab_case="user-profile-id",
        train_case="User-Profile-Id",
        flat_case="userprofileid",
        dot_case="user.profile.id",
        title_case="User Profile Id",
        path_case="user/profile/id",
    ),
    Case(
        value="API response-code error",
        upper_case="API RESPONSE-CODE ERROR",
        lower_case="api response-code error",
        meme_case="aPi ReSpOnSe-CoDe ErRoR",
        snake_case="api_response_code_error",
        screaming_snake_case="API_RESPONSE_CODE_ERROR",
        camel_case="apiResponseCodeError",
        pascal_case="ApiResponseCodeError",
        kebab_case="api-response-code-error",
        train_case="Api-Response-Code-Error",
        flat_case="apiresponsecodeerror",
        dot_case="api.response.code.error",
        title_case="Api Response Code Error",
        path_case="api/response/code/error",
    ),
    Case(
        value="version2 updateLog",
        upper_case="VERSION2 UPDATELOG",
        lower_case="version2 updatelog",
        meme_case="vErSiOn2 UpDaTeLoG",
        snake_case="version2_update_log",
        screaming_snake_case="VERSION2_UPDATE_LOG",
        camel_case="version2UpdateLog",
        pascal_case="Version2UpdateLog",
        kebab_case="version2-update-log",
        train_case="Version2-Update-Log",
        flat_case="version2updatelog",
        dot_case="version2.update.log",
        title_case="Version2 Update Log",
        path_case="version2/update/log",
    ),
    Case(
        value="Load XML File",
        upper_case="LOAD XML FILE",
        lower_case="load xml file",
        meme_case="lOaD xMl FiLe",
        snake_case="load_xml_file",
        screaming_snake_case="LOAD_XML_FILE",
        camel_case="loadXmlFile",
        pascal_case="LoadXmlFile",
        kebab_case="load-xml-file",
        train_case="Load-Xml-File",
        flat_case="loadxmlfile",
        dot_case="load.xml.file",
        title_case="Load Xml File",
        path_case="load/xml/file",
    ),
    Case(
        value="  file.name_v2--FINAL  ",
        upper_case="FILE.NAME_V2--FINAL",
        lower_case="file.name_v2--final",
        meme_case="fIlE.nAmE_v2--FiNaL",
        snake_case="file_name_v2_final",
        screaming_snake_case="FILE_NAME_V2_FINAL",
        camel_case="fileNameV2Final",
        pascal_case="FileNameV2Final",
        kebab_case="file-name-v2-final",
        train_case="File-Name-V2-Final",
        flat_case="filenamev2final",
        dot_case="file.name.v2.final",
        title_case="File Name V2 Final",
        path_case="file/name/v2/final",
    ),
    Case(
        value="🔥 boost-mode 3000!! ready_to-GO",
        upper_case="🔥 BOOST-MODE 3000!! READY_TO-GO",
        lower_case="🔥 boost-mode 3000!! ready_to-go",
        meme_case="🔥 bOoSt-MoDe 3000!! ReAdY_tO-gO",
        snake_case="boost_mode_3000_ready_to_go",
        screaming_snake_case="BOOST_MODE_3000_READY_TO_GO",
        camel_case="boostMode3000ReadyToGo",
        pascal_case="BoostMode3000ReadyToGo",
        kebab_case="boost-mode-3000-ready-to-go",
        train_case="Boost-Mode-3000-Ready-To-Go",
        flat_case="boostmode3000readytogo",
        dot_case="boost.mode.3000.ready.to.go",
        title_case="Boost Mode 3000 Ready To Go",
        path_case="boost/mode/3000/ready/to/go",
    ),
    Case(
        value="Café—注文#42 ready•NOW",
        upper_case="CAFÉ—注文#42 READY•NOW",
        lower_case="café—注文#42 ready•now",
        meme_case="cAfÉ—注文#42 rEaDy•NoW",
        snake_case="cafe_注文_42_ready_now",
        screaming_snake_case="CAFE_注文_42_READY_NOW",
        camel_case="cafe注文42ReadyNow",
        pascal_case="Cafe注文42ReadyNow",
        kebab_case="cafe-注文-42-ready-now",
        train_case="Cafe-注文-42-Ready-Now",
        flat_case="cafe注文42readynow",
        dot_case="cafe.注文.42.ready.now",
        title_case="Cafe 注文 42 Ready Now",
        path_case="cafe/注文/42/ready/now",
    ),
    Case(
        value="[config]/User-Data v1.0: INIT",
        upper_case="CONFIG/USER-DATA V1.0: INIT",
        lower_case="config/user-data v1.0: init",
        meme_case="[cOnFiG]/uSeR-dAtA v1.0: InIt",
        snake_case="config_user_data_v1_0_init",
        screaming_snake_case="CONFIG_USER_DATA_V1_0_INIT",
        camel_case="configUserDataV10Init",
        pascal_case="ConfigUserDataV10Init",
        kebab_case="config-user-data-v1-0-init",
        train_case="Config-User-Data-V1-0-Init",
        flat_case="configuserdatav10init",
        dot_case="config.user.data.v1.0.init",
        title_case="Config User Data V1 0 Init",
        path_case="config/user/data/v1/0/init",
    ),
    Case(
        value=" next\tstep → FINAL_stage--beta ",
        upper_case="NEXT STEP → FINAL_STAGE--BETA",
        lower_case="next step → final_stage--beta",
        meme_case="nExT\tsTeP → fInAl_StAgE--bEtA",
        snake_case="next_step_final_stage_beta",
        screaming_snake_case="NEXT_STEP_FINAL_STAGE_BETA",
        camel_case="nextStepFinalStageBeta",
        pascal_case="NextStepFinalStageBeta",
        kebab_case="next-step-final-stage-beta",
        train_case="Next-Step-Final-Stage-Beta",
        flat_case="nextstepfinalstagebeta",
        dot_case="next.step.final.stage.beta",
        title_case="Next Step Final Stage Beta",
        path_case="next/step/final/stage/beta",
    ),
    Case(
        value="sum_total::VAL-99 ≈ ready.now",
        upper_case="SUM_TOTAL::VAL-99 ≈ READY.NOW",
        lower_case="sum_total::val-99 ≈ ready.now",
        meme_case="sUm_ToTaL::vAl-99 ≈ ReAdY.nOw",
        snake_case="sum_total_val_99_ready_now",
        screaming_snake_case="SUM_TOTAL_VAL_99_READY_NOW",
        camel_case="sumTotalVal99ReadyNow",
        pascal_case="SumTotalVal99ReadyNow",
        kebab_case="sum-total-val-99-ready-now",
        train_case="Sum-Total-Val-99-Ready-Now",
        flat_case="sumtotalval99readynow",
        dot_case="sum.total.val.99.ready.now",
        title_case="Sum Total Val 99 Ready Now",
        path_case="sum/total/val/99/ready/now",
    ),
    Case(
        value="Hello World This is prettY coOL",
        upper_case="HELLO WORLD THIS IS PRETTY COOL",
        lower_case="hello world this is pretty cool",
        meme_case="hElLo WoRlD tHiS iS pReTtY cOoL",
        snake_case="hello_world_this_is_pretty_cool",
        screaming_snake_case="HELLO_WORLD_THIS_IS_PRETTY_COOL",
        camel_case="helloWorldThisIsPrettyCool",
        pascal_case="HelloWorldThisIsPrettyCool",
        kebab_case="hello-world-this-is-pretty-cool",
        train_case="Hello-World-This-Is-Pretty-Cool",
        flat_case="helloworldthisisprettycool",
        dot_case="hello.world.this.is.pretty.cool",
        title_case="Hello World This Is Pretty Cool",
        path_case="hello/world/this/is/pretty/cool",
    ),
]


class TestLowerCase:
    """Test the lower case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_lower_case(case.value) == case.lower_case


class TestUpperCase:
    """Test the upper case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_upper_case(case.value) == case.upper_case


class TestMemeCase:
    """Test the meme case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_meme_case(case.value) == case.meme_case


class TestSnakeCase:
    """Test the snake case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_snake_case(case.value) == case.snake_case


class TestScreamingSnakeCase:
    """Test the screaming snake case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert (
                Casing.to_screaming_snake_case(case.value)
                == case.screaming_snake_case
            )


class TestCamelCase:
    """Test the camel case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_camel_case(case.value) == case.camel_case


class TestPascalCase:
    """Test the pascal case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_pascal_case(case.value) == case.pascal_case


class TestKebabCase:
    """Test the kebab case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_kebab_case(case.value) == case.kebab_case


class TestTrainCase:
    """Test the train case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_train_case(case.value) == case.train_case


class TestFlatCaase:
    """Test the flat case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_flat_case(case.value) == case.flat_case


class TestDotCase:
    """Test the dot case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_dot_case(case.value) == case.dot_case


class TestTitleCase:
    """Test the pascal case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_title_case(case.value) == case.title_case


class TestPathCase:
    """Test the path case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            assert Casing.to_path_case(case.value) == case.path_case
