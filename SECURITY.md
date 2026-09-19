# Security policy

This repository supplies `dtutila/hyprland`. Review and release procedures are in
[docs/security-audit.md](docs/security-audit.md). Do not interpret successful
package builds as a complete audit of the compositor, authentication or locker.

A private security contact has not been designated. Arrange a private reporting
channel with the project owner before sharing exploit details or credentials;
do not place those details in public packaging issues. Ordinary non-security
packaging defects may use the repository's issue tracker.

Never commit COPR credentials, forge tokens, signing material or private keys.
If exposed, revoke them immediately; deleting the latest Git revision is not
sufficient. Build containers must not receive production credentials.
