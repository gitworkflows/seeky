#![expect(clippy::expect_used)]
use seeky_execpolicy::ArgMatcher;
use seeky_execpolicy::ArgType;
use seeky_execpolicy::Error;
use seeky_execpolicy::ExecCall;
use seeky_execpolicy::MatchedArg;
use seeky_execpolicy::MatchedExec;
use seeky_execpolicy::MatchedOpt;
use seeky_execpolicy::Policy;
use seeky_execpolicy::Result;
use seeky_execpolicy::ValidExec;
use seeky_execpolicy::get_default_policy;

extern crate seeky_execpolicy;

fn setup() -> Policy {
    get_default_policy().expect("failed to load default policy")
}

#[test]
fn test_head_no_args() {
    let policy = setup();
    let head = ExecCall::new("head", &[]);
    // It is actually valid to call `head` without arguments: it will read from
    // stdin instead of from a file. Though recall that a command rejected by
    // the policy is not "unsafe:" it just means that this library cannot
    // *guarantee* that the command is safe.
    //
    // If we start verifying individual components of a shell command, such as:
    // `find . -name | head -n 10`, then it might be important to allow the
    // no-arg case.
    assert_eq!(
        Err(Error::VarargMatcherDidNotMatchAnything {
            program: "head".to_string(),
            matcher: ArgMatcher::ReadableFiles,
        }),
        policy.check(&head)
    )
}

#[test]
fn test_head_one_file_no_flags() -> Result<()> {
    let policy = setup();
    let head = ExecCall::new("head", &["src/extension.ts"]);
    assert_eq!(
        Ok(MatchedExec::Match {
            exec: ValidExec::new(
                "head",
                vec![MatchedArg::new(
                    0,
                    ArgType::ReadableFile,
                    "src/extension.ts"
                )?],
                &["/bin/head", "/usr/bin/head"]
            )
        }),
        policy.check(&head)
    );
    Ok(())
}

#[test]
fn test_head_one_flag_one_file() -> Result<()> {
    let policy = setup();
    let head = ExecCall::new("head", &["-n", "100", "src/extension.ts"]);
    assert_eq!(
        Ok(MatchedExec::Match {
            exec: ValidExec {
                program: "head".to_string(),
                flags: vec![],
                opts: vec![
                    MatchedOpt::new("-n", "100", ArgType::PositiveInteger)
                        .expect("should validate")
                ],
                args: vec![MatchedArg::new(
                    2,
                    ArgType::ReadableFile,
                    "src/extension.ts"
                )?],
                system_path: vec!["/bin/head".to_string(), "/usr/bin/head".to_string()],
            }
        }),
        policy.check(&head)
    );
    Ok(())
}

#[test]
fn test_head_invalid_n_as_0() {
    let policy = setup();
    let head = ExecCall::new("head", &["-n", "0", "src/extension.ts"]);
    assert_eq!(
        Err(Error::InvalidPositiveInteger {
            value: "0".to_string(),
        }),
        policy.check(&head)
    )
}

#[test]
fn test_head_invalid_n_as_nonint_float() {
    let policy = setup();
    let head = ExecCall::new("head", &["-n", "1.5", "src/extension.ts"]);
    assert_eq!(
        Err(Error::InvalidPositiveInteger {
            value: "1.5".to_string(),
        }),
        policy.check(&head)
    )
}

#[test]
fn test_head_invalid_n_as_float() {
    let policy = setup();
    let head = ExecCall::new("head", &["-n", "1.0", "src/extension.ts"]);
    assert_eq!(
        Err(Error::InvalidPositiveInteger {
            value: "1.0".to_string(),
        }),
        policy.check(&head)
    )
}

#[test]
fn test_head_invalid_n_as_negative_int() {
    let policy = setup();
    let head = ExecCall::new("head", &["-n", "-1", "src/extension.ts"]);
    assert_eq!(
        Err(Error::OptionFollowedByOptionInsteadOfValue {
            program: "head".to_string(),
            option: "-n".to_string(),
            value: "-1".to_string(),
        }),
        policy.check(&head)
    )
}
