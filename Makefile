AWS_DIR   := app/cumulonimbus/applications/aws
AZURE_DIR := app/cumulonimbus/applications/azure
CTFD_DIR  := ctfd

LAB ?=

.PHONY: help ctfd ctfd-aws ctfd-azure ctfd-stop labs lab destroy clean

# ── Default ───────────────────────────────────────────────────────────────────
help:
	@printf "\033[1mCumulonimbus — Cloud Attack Range\033[0m\n\n"
	@printf "\033[1mCTFd\033[0m\n"
	@printf "  \033[36mmake ctfd\033[0m               Start both CTFd instances and seed all challenges\n"
	@printf "  \033[36mmake ctfd-aws\033[0m           Start the AWS  instance only  (http://localhost:8000)\n"
	@printf "  \033[36mmake ctfd-azure\033[0m         Start the Azure instance only (http://localhost:8001)\n"
	@printf "  \033[36mmake ctfd-stop\033[0m          Stop all CTFd containers\n\n"
	@printf "\033[1mLabs\033[0m\n"
	@printf "  \033[36mmake labs\033[0m               List all available labs\n"
	@printf "  \033[36mmake lab   LAB=<id>\033[0m     Deploy a lab (provider is detected automatically)\n"
	@printf "  \033[36mmake destroy LAB=<id>\033[0m   Destroy a lab\n\n"
	@printf "\033[1mMaintenance\033[0m\n"
	@printf "  \033[36mmake clean\033[0m              Stop CTFd and remove all containers and volumes\n\n"
	@printf "Examples:\n"
	@printf "  make lab LAB=ec2_ssrf\n"
	@printf "  make lab LAB=keyvault_misconfig\n"
	@printf "  make destroy LAB=ec2_ssrf\n"

# ── CTFd ──────────────────────────────────────────────────────────────────────
ctfd:
	@printf "\033[1mStarting CTFd containers...\033[0m\n"
	@cd $(CTFD_DIR) && docker compose up -d
	@printf "\033[1mSeeding AWS challenges...\033[0m\n"
	@cd $(CTFD_DIR) && python3 setup.py --provider aws
	@printf "\033[1mSeeding Azure challenges...\033[0m\n"
	@cd $(CTFD_DIR) && python3 setup.py --provider azure
	@printf "\n\033[32m✓ CTFd is ready\033[0m\n"
	@printf "  AWS   → http://localhost:8000  (admin / cumulonimbus)\n"
	@printf "  Azure → http://localhost:8001  (admin / cumulonimbus)\n\n"

ctfd-aws:
	@cd $(CTFD_DIR) && docker compose up -d ctfd_aws db_aws cache_aws
	@cd $(CTFD_DIR) && python3 setup.py --provider aws
	@printf "\n\033[32m✓ AWS CTFd ready → http://localhost:8000\033[0m\n\n"

ctfd-azure:
	@cd $(CTFD_DIR) && docker compose up -d ctfd_azure db_azure cache_azure
	@cd $(CTFD_DIR) && python3 setup.py --provider azure
	@printf "\n\033[32m✓ Azure CTFd ready → http://localhost:8001\033[0m\n\n"

ctfd-stop:
	@cd $(CTFD_DIR) && docker compose stop
	@printf "\033[32m✓ CTFd stopped\033[0m\n"

# ── Labs ──────────────────────────────────────────────────────────────────────
labs:
	@python3 scripts/labs.py

lab:
	@test -n "$(LAB)" || \
		(printf "\033[31mError:\033[0m no lab specified.\n  Usage: make lab LAB=<id>\n  Hint:  run 'make labs' to see all available labs\n" && exit 1)
	@if [ -d "$(AWS_DIR)/$(LAB)" ]; then \
		printf "\033[1mDeploying AWS lab:\033[0m $(LAB)\n"; \
		cnimbus aws create --app-id $(LAB); \
	elif [ -d "$(AZURE_DIR)/$(LAB)" ]; then \
		printf "\033[1mDeploying Azure lab:\033[0m $(LAB)\n"; \
		cnimbus azure create --app-id $(LAB); \
	else \
		printf "\033[31mError:\033[0m unknown lab '$(LAB)'.\n  Run 'make labs' to see all available labs.\n" && exit 1; \
	fi

destroy:
	@test -n "$(LAB)" || \
		(printf "\033[31mError:\033[0m no lab specified.\n  Usage: make destroy LAB=<id>\n" && exit 1)
	@if [ -d "$(AWS_DIR)/$(LAB)" ]; then \
		printf "\033[1mDestroying AWS lab:\033[0m $(LAB)\n"; \
		cnimbus aws destroy --app-id $(LAB); \
	elif [ -d "$(AZURE_DIR)/$(LAB)" ]; then \
		printf "\033[1mDestroying Azure lab:\033[0m $(LAB)\n"; \
		cnimbus azure destroy --app-id $(LAB); \
	else \
		printf "\033[31mError:\033[0m unknown lab '$(LAB)'.\n  Run 'make labs' to see all available labs.\n" && exit 1; \
	fi

# ── Maintenance ───────────────────────────────────────────────────────────────
clean:
	@printf "\033[1mStopping CTFd and removing all volumes...\033[0m\n"
	@cd $(CTFD_DIR) && docker compose down -v
	@printf "\033[32m✓ Done\033[0m\n"
